import pandas as pd
import textwrap

import us

from ..base import ArcGIS
from ... import DatasetBaseNoDate


class Texas(DatasetBaseNoDate, ArcGIS):
    ARCGIS_ID = "ACaLB9ifngzawspq"
    source = (
        "https://txdshs.maps.arcgis.com/apps/opsdashboard/index.html"
        "#/ed483ecd702b4298ab01e8b9cafc8b83"
    )
    state_fips = int(us.states.lookup("Texas").fips)
    has_fips = True

    def _get_tests(self):
        df = self.get_all_sheet_to_df(
            "DSHS_COVID19_TestData_Service", 3, 5
        ).rename(columns={
            "Date": "dt",
            "ViralTests": "tests_total",
        })

        df["dt"] = df["dt"].map(lambda x: self._esri_ts_to_dt(x))
        df["fips"] = self.state_fips

        df = df.loc[:, ["dt", "fips", "tests_total"]]
        out = df.melt(
            id_vars=["dt", "fips"], var_name="variable_name"
        ).dropna()
        out["value"] = out["value"].astype(int)

        return out

    def get(self):
        test = self._get_tests()

        out = pd.concat([test], axis=0, ignore_index=True)
        out["vintage"] = self._retrieve_vintage()

        return out


class TexasCounty(DatasetBaseNoDate, ArcGIS):
    ARCGIS_ID = "ACaLB9ifngzawspq"
    source = (
        "https://txdshs.maps.arcgis.com/apps/opsdashboard/index.html"
        "#/ed483ecd702b4298ab01e8b9cafc8b83"
    )
    state_fips = int(us.states.lookup("Texas").fips)
    has_fips = False

    def _get_cases_deaths(self):
        crename = {
            "dt": "dt",
            "County": "county",
            "Positive": "cases_total",
            "Fatalities": "deaths_total",
            "Recoveries": "recovered_total",
            "Active": "active_total",
        }
        df = self.get_all_sheet_to_df(
            "DSHS_COVID19_Cases_Service", 0, 5
        ).rename(columns=crename)
        df["dt"] = self._retrieve_dt("US/Central")

        df = df.loc[:, crename.values()]
        out = df.melt(
            id_vars=["dt", "county"], var_name="variable_name"
        ).dropna()
        out["value"] = out["value"].astype(int)

        return out

    def _get_tests(self):
        df = self.get_all_sheet_to_df(
            "DSHS_COVID19_TestData_Service", 0, 5
        ).rename(columns={
            "County": "county",
            "ViralTest": "tests_total",
        })

        df["dt"] = self._retrieve_dt("US/Central")

        df = df.loc[:, ["dt", "county", "tests_total"]]
        out = df.melt(
            id_vars=["dt", "county"], var_name="variable_name"
        ).dropna()
        out["value"] = out["value"].astype(int)

        return out

    def get(self):
        cdra = self._get_cases_deaths()
        test = self._get_tests()

        out = pd.concat([cdra, test], axis=0, ignore_index=True)
        out["vintage"] = self._retrieve_vintage()

        return out
