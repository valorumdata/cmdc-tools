import pandas as pd
import textwrap
import us

from ... import ArcGIS
from .... import DatasetBaseNoDate



class MOStLouis(DatasetBaseNoDate, ArcGIS):
    """
    St Louis, Missouri publishes their county level data in a
    dashboard that can be found at:

    https://data-stlcogis.opendata.arcgis.com/app/st-louis-county-covid-19-statistics

    This retrieves the data from the ArcGIS API
    """

    ARCGIS_ID = "w657bnjzrjguNyOy"
    source = "https://stlcorona.com/resources/covid-19-statistics1/"
    county_fips = 189  # St. Louis Cnty	189 <--- NOT St. Louis City
    state_fips = int(us.states.lookup("MO").fips)
    has_fips = True
    provider = "county"

    def _get_cases(self):
        # Case data
        df_cases = self.get_all_sheet_to_df("covid19_timeline_test", 0, 2)
        df_cases["dt"] = df_cases["report_date"].map(
            lambda x: self._esri_ts_to_dt(x)
        )
        df_cases = df_cases.rename(columns={"cumulative_cases": "cases_total"})

        out = df_cases.loc[:, ["dt", "cases_total"]].melt(
            id_vars="dt", var_name="variable_name"
        )

        return out

    def _get_deaths(self):
        # Death data
        df_deaths = self.get_all_sheet_to_df("covid19_deaths_timeline", 0, 2)
        df_deaths["dt"] = df_deaths["date_of_death"].map(
            lambda x: self._esri_ts_to_dt(x)
        )
        df_deaths = df_deaths.sort_values("dt")
        df_deaths["deaths_total"] = df_deaths["deaths"].cumsum()

        out = df_deaths.loc[:, ["dt", "deaths_total"]].melt(
            id_vars="dt", var_name="variable_name"
        )

        return out

    def _get_tests(self):
        df_tests = self.get_all_sheet_to_df("covid19_labs_daily", 0, 2)
        df_tests["dt"] = df_tests["test_date"].map(
            lambda x: self._esri_ts_to_dt(x)
        )
        df_tests = df_tests.sort_values("dt")

        df_tests["negative_tests_total"] = df_tests["negative"].cumsum()
        df_tests["positive_tests_total"] = df_tests["positive"].cumsum()
        df_tests["tests_total"] = df_tests.eval(
            "negative_tests_total + positive_tests_total"
        )

        _vars = ["dt", "negative_tests_total", "positive_tests_total"]
        out = df_tests.loc[:, _vars].melt(
            id_vars="dt", var_name="variable_name"
        )

        return out

    def get(self):

        df = pd.concat(
            [
                self._get_cases(),
                self._get_deaths(),
                self._get_tests()
            ], axis=0, ignore_index=True
        )
        df["vintage"] = self._retrieve_vintage()
        df["fips"] = self.state_fips*1000 + self.county_fips

        return df
