import datetime
import requests

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
    "https://wabi-us-gov-virginia-api.analysis.usgovcloudapi.net"
    "/public/reports/querydata?synchronous=true"
)


def run_query_for_county(county):
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
                    "DatasetId": "bbf92461-0df5-47fe-a03a-1cbd0c0e3ff4",
                    "Sources": [{"ReportId": "bbf92461-0df5-47fe-a03a-1cbd0c0e3ff4"}],
                },
            }
        ],
        "cancelQueries": [],
        "modelId": 380424,
    }

    headers = {"X-PowerBI-ResourceKey": "5ad03247-b18b-4ef8-9dca-fd4bcb2f4cef"}
    return requests.post(DASHBOARD_URL, headers=headers, json=data).json()


def parse_row(row):

    row = row["C"] + [None] * (4 - len(row["C"]))
    timestamp, _, _, current_hosp = row
    return {
        "dt": datetime.datetime.utcfromtimestamp(timestamp / 1000).date(),
        "variable_name": "hospital_beds_in_use_covid_total",
        "value": current_hosp,
    }


def _unwrap_results(results):
    return results["results"][0]["result"]["data"]["dsr"]["DS"][0]["PH"][0]["DM0"]


def main(counties=None):
    counties = counties or WA_COUNTIES
    all_rows = []
    for county in WA_COUNTIES:

        results = run_query_for_county(county)
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
