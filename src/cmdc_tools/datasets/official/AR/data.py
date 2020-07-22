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
    has_fips = True

    def get(self):
        df = self.get_all_sheet_to_df(
            service="ADH_COVID19_Positive_Test_Results", sheet=0, srvid=""
        )
        df = df.query("county_nam != 'Missing County Info'")

        # Filter columns
        crename = {
            "FIPS": "fips",
            "positive": "positive_tests_total",
            "negative": "negative_tests_total",
            "total_tests": "tests_total",
            "Recoveries": "recovered_total",
            "deaths": "deaths_total",
            "active_cases": "active_total",
        }
        df = df.rename(columns=crename).loc[:, crename.values()]

        # Create full 5 digit fips
        df["fips"] = df["fips"].astype(int) + 1000*self.state_fips

        df["vintage"] = self._retrieve_vintage()
        df["dt"] = self._retrieve_dt(tz="US/Central")

        out = df.melt(
            id_vars=["vintage", "dt", "fips"],
            var_name="variable_name",
            value_name="value",
        )

        return out
