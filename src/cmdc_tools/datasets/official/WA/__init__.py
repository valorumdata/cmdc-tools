from typing import Optional, List
import urllib.parse
import datetime
import base64
import dataclasses
import json


import requests
import bs4
import pandas as pd
import us

from ... import DatasetBaseNoDate
from .. import CountyData


WA_COUNTIES = [
    "Adams",
    "Asotin",
    "Benton",
    "Chelan",
    "Clallam",
    "Clark",
    "Columbia",
    "Cowlitz",
    "Douglas",
    "Ferry",
    "Franklin",
    "Garfield",
    "Grant",
    "Grays Harbor",
    "Island",
    "Jefferson",
    "King",
    "Kitsap",
    "Kittitas",
    "Klickitat",
    "Lewis",
    "Lincoln",
    "Mason",
    "Okanogan",
    "Pacific",
    "Pend Oreille",
    "Pierce",
    "San Juan",
    "Skagit",
    "Skamania",
    "Snohomish",
    "Spokane",
    "Stevens",
    "Thurston",
    "Wahkiakum",
    "Walla Walla",
    "Whatcom",
    "Whitman",
    "Yakima",
]


DASHBOARD_URL = (
    "https://coronavirus.wa.gov/what-you-need-know/covid-19-risk-assessment-dashboard"
)

POWER_BI_DASHBOARD_ENDPOINT = (
    "https://wabi-us-gov-virginia-api.analysis.usgovcloudapi.net"
    "/public/reports/querydata?synchronous=true"
)


@dataclasses.dataclass
class PowerBIQueryDetails:
    """IDs needed to query latest version of Power BI objects."""

    resource_key: str
    model_id: int
    database_id: str
    report_id: str


def _get_resource_key(wa_dashboard_url: str) -> str:
    # The resource key is base64 encoded in the iframe url for the dashboard.
    wa_data_html = requests.get(wa_dashboard_url).content
    wa_parsed_page = bs4.BeautifulSoup(wa_data_html)
    url = wa_parsed_page.find("iframe", {"id": "CovidDashboardFrame"}).parent[
        "pbi-resize-src"
    ]
    parsed_url = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(parsed_url.query)
    parsed = json.loads(base64.b64decode(query["r"][0]))
    return parsed["k"]


def _get_query_details(wa_dashboard_url: str) -> PowerBIQueryDetails:
    resource_key = _get_resource_key(wa_dashboard_url)
    headers = {"X-PowerBI-ResourceKey": resource_key}
    data = requests.get(
        "https://wabi-us-gov-virginia-api.analysis.usgovcloudapi.net/public/reports/"
        f"{resource_key}/modelsAndExploration?preferReadOnlySession=true",
        headers=headers,
    ).json()

    model = data["models"][0]

    return PowerBIQueryDetails(
        resource_key=resource_key,
        model_id=model["id"],
        database_id=model["dbName"],
        report_id=data["exploration"]["report"]["objectId"],
    )


def run_query_for_county(query_details: PowerBIQueryDetails, county: str) -> dict:
    query = {
        "Query": {
            "Version": 2,
            "From": [
                {"Name": "c1", "Entity": "cds_covid", "Type": 0},
                {"Name": "_", "Entity": "_counties", "Type": 0},
            ],
            "Select": [
                {
                    "Column": {
                        "Expression": {"SourceRef": {"Source": "c1"}},
                        "Property": "Date",
                    },
                    "Name": "cds_covid.Date",
                },
                {
                    "Measure": {
                        "Expression": {"SourceRef": {"Source": "c1"}},
                        "Property": "#perc_occupied_covid_after",
                    },
                    "Name": "cds_covid.#perc_occupied_covid",
                },
                {
                    "Measure": {
                        "Expression": {"SourceRef": {"Source": "c1"}},
                        "Property": "#7day_movingaverage",
                    },
                    "Name": "cds_covid.###7daytotal",
                },
                {
                    "Aggregation": {
                        "Expression": {
                            "Column": {
                                "Expression": {"SourceRef": {"Source": "c1"}},
                                "Property": "total_covid_patients",
                            }
                        },
                        "Function": 0,
                    },
                    "Name": "Sum(cds_covid.total_covid_patients)",
                },
            ],
            "Where": [
                {
                    "Condition": {
                        "In": {
                            "Expressions": [
                                {
                                    "Column": {
                                        "Expression": {"SourceRef": {"Source": "_"}},
                                        "Property": "County",
                                    }
                                }
                            ],
                            "Values": [[{"Literal": {"Value": f"'{county}'"}}]],
                        }
                    }
                }
            ],
            "OrderBy": [
                {
                    "Direction": 2,
                    "Expression": {
                        "Column": {
                            "Expression": {"SourceRef": {"Source": "c1"}},
                            "Property": "Date",
                        }
                    },
                }
            ],
        },
        "Binding": {
            "Primary": {"Groupings": [{"Projections": [0, 1, 2, 3]}]},
            "DataReduction": {"DataVolume": 3, "Primary": {"Window": {"Count": 500}},},
            "Version": 1,
        },
    }

    data = {
        "version": "1.0.0",
        "queries": [
            {
                "Query": {"Commands": [{"SemanticQueryDataShapeCommand": query}]},
                "QueryId": "",
                "ApplicationContext": {
                    "DatasetId": query_details.database_id,
                    "Sources": [{"ReportId": query_details.report_id}],
                },
            }
        ],
        "cancelQueries": [],
        "modelId": query_details.model_id,
    }

    headers = {"X-PowerBI-ResourceKey": query_details.resource_key}
    return requests.post(POWER_BI_DASHBOARD_ENDPOINT, headers=headers, json=data).json()


def parse_row(row: dict) -> dict:

    row = row["C"] + [None] * (4 - len(row["C"]))
    timestamp, _, _, current_hosp = row
    return {
        "dt": datetime.datetime.utcfromtimestamp(timestamp / 1000).date(),
        "variable_name": "hospital_beds_in_use_covid_total",
        "value": current_hosp,
    }


def _unwrap_results(results: dict) -> List[dict]:
    return results["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"]


def main(counties: Optional[List[str]] = None) -> List[dict]:

    power_bi_query_details = _get_query_details(DASHBOARD_URL)

    counties = counties or WA_COUNTIES
    all_rows = []
    for county in counties:

        results = run_query_for_county(power_bi_query_details, county)
        for row in _unwrap_results(results):
            row = parse_row(row)
            row["county"] = county
            all_rows.append(row)

    return all_rows


class Washington(DatasetBaseNoDate, CountyData):
    source = "https://coronavirus.wa.gov/what-you-need-know/covid-19-risk-assessment-dashboard"
    state_fips = int(us.states.lookup("Washington").fips)
    has_fips = False
    url = "https://www.doh.wa.gov/Emergencies/COVID19/DataDashboard"

    def get(self) -> pd.DataFrame:
        return pd.DataFrame(main()).assign(
            vintage=self._retrieve_vintage(), dt=lambda x: pd.to_datetime(x["dt"])
        )
