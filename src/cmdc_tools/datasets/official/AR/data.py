import textwrap

import pandas as pd
import requests
import us

from ..base import ArcGIS
from ...base import DatasetBaseNoDate


class Arkansas(DatasetBaseNoDate, ArcGIS):
    ARCGIS_ID = "PwY9ZuZRDiI5nXUB"
    source = "https://experience.arcgis.com/experience/c2ef4a4fcbe5458fbf2e48a21e4fece9"
    state_fips = int(us.states.lookup("Arkansas").fips)
    has_fips = False

    def __init__(self, params=None):

        if params is None:
            params = {
                "f": "json",
                "where": "1=1",
                "outFields": "*",
                "returnGeometry": "false",
            }

        super(Arkansas, self).__init__(params)

    def get(self):
        url = self.arcgis_query_url(
            service="ADH_COVID19_Positive_Test_Results", sheet=0, srvid=""
        )
        res = requests.get(url, params=self.params)

        df = pd.DataFrame.from_records(
            [x["attributes"] for x in res.json()["features"]]
        )

        # Filter columns
        crename = {
            "county_nam": "county",
            "positive": "positive_tests_total",
            "negative": "negative_tests_total",
            "Recoveries": "recovered_total",
            "deaths": "deaths_total",
            "active_cases": "active_total",
        }
        keep = df.rename(columns=crename)

        keeprows = ~keep["county"].str.lower().str.contains("missing")
        keep = keep.loc[keeprows, crename.values()]

        keep["vintage"] = pd.datetime.today().date()
        keep["dt"] = pd.datetime.today().date()
        keep = keep.melt(
            id_vars=["vintage", "dt", "county"],
            var_name="variable_name",
            value_name="value",
        )

        return keep
