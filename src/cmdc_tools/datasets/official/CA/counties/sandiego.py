import requests
import pandas as pd

from ... import ArcGIS
from .... import DatasetBaseNoDate


class SanDiego(DatasetBaseNoDate, ArcGIS):
    """
    San Diego publishes their county level data in a dashboard that can
    be found at:

    https://www.sandiegocounty.gov/content/sdc/hhsa/programs/phs/community_epidemiology/dc/2019-nCoV/status.html

    They don't seem to provide any simple interface to their data...
    However, one can directly request data from arcgis itself which is
    the route we take here. The San Diego arcgis service called
    `CovidDashUpdate` had all relevant data within it, so we can only use
    the one for now
    """

    ARCGIS_ID = "1vIhDJwtG5eNmiqX"
    FIPS = 6073
    source = (
        "https://www.sandiegocounty.gov/content/sdc/hhsa/programs"
        "/phs/community_epidemiology/dc/2019-nCoV/status.html"
    )
    state_fips = 6

    def __init__(self, params=None):
        # Default parameter values
        if params is None:
            params = {
                "where": "0=0",
                "outFields": "Date,Tests,Positives",
                "returnGeometry": "false",
                "f": "pjson",
            }

        super(SanDiego, self).__init__(params=params)

        return None

    def get(self):

        _url = self.arcgis_query_url("CovidDashUpdate", 1)
        req = requests.get(_url, params=self.params)

        # Read into dataframe
        df = pd.DataFrame.from_records(
            [x["attributes"] for x in req.json()["features"]]
        )
        # Divide by 1000 because arcgis spits time out in epoch milliseconds
        # rather than epoch seconds
        df["Date"] = df["Date"].map(lambda x: pd.datetime.fromtimestamp(x / 1000))
        df["vintage"] = pd.datetime.today()
        df["fips"] = self.FIPS

        # Rename columns
        df = df.rename(
            columns={
                "Date": "dt",
                "Tests": "tests_total",
                "Positives": "positive_tests_total",
            }
        )
        df["negative_tests_total"] = df.eval("tests_total - positive_tests_total")
        df = df[
            ["vintage", "dt", "fips", "positive_tests_total", "negative_tests_total"]
        ]

        df = df.melt(
            id_vars=["vintage", "dt", "fips"],
            var_name="variable_name",
            value_name="value",
        )

        return df
