import pandas as pd
import us

from ...base import DatasetBaseNoDate
from ..base import ArcGIS


class Colorado(DatasetBaseNoDate, ArcGIS):
    ARCGIS_ID = "66aUo8zsujfVXRIT"
    source = "https://services3.arcgis.com/66aUo8zsujfVXRIT/arcgis/rest/services/"
    has_fips = True
    state_fips = int(us.states.lookup("Colorado").fips)

    def _convert_dt(self, series):
        return (
            pd.to_datetime(series)
            .dt.tz_localize("America/Denver")
            .dt.tz_convert("UTC")
            .dt.normalize()
        )

    def get(self):
        county_stats = self._get_county_stats()
        state_stats = self._get_stats()
        tests = self._get_tests()

        return pd.concat([county_stats, state_stats, tests], sort=False).sort_values(
            ["dt", "fips"]
        )

    def _get_county_stats(self):
        df = self.get_all_sheet_to_df(
            "colorado_covid19_county_statistics_cumulative", 0, 3
        )
        keep_rows = ["Cases", "Deaths", "Total Tests Performed"]
        filtered = df.loc[df.Metric.isin(keep_rows)]
        renamed = filtered.rename(
            columns={
                "Value": "value",
                "Date": "dt",
                "FIPS": "fips",
                "Metric": "variable_name",
            }
        )

        renamed.dt = self._convert_dt(renamed.dt)
        renamed.value = renamed.value.astype(int)
        # Filter out fips == none
        renamed = renamed.dropna(subset=["fips"])
        renamed.fips = renamed.fips.astype(int) + (self.state_fips * 1000)

        var_rename = {
            "Cases": "cases_total",
            "Total Tests Performed": "tests_total",
            "Deaths": "deaths_total",
        }
        renamed.variable_name = renamed.variable_name.replace(var_rename)
        return (
            renamed[["dt", "fips", "variable_name", "value"]]
            .assign(vintage=pd.Timestamp.utcnow())
            .sort_values(["dt", "fips", "variable_name"])
        )

    def _get_tests(self):
        df = self.get_all_sheet_to_df(
            "colorado_covid19_laboratory_positivity_data", 0, 3
        )
        keep_rows = [
            "Number of positive tests",
            "Number of negative tests",
        ]

        filtered = df.loc[df.Metric.isin(keep_rows)]
        renamed = filtered.rename(
            columns={"Attr_Date": "dt", "Metric": "variable_name", "Value": "value"}
        )
        renamed.value = renamed.value.astype(int)
        renamed["fips"] = self.state_fips
        renamed.dt = self._convert_dt(renamed.dt)
        var_rename = {
            "Number of positive tests": "positive_tests_total",
            "Number of negative tests": "negative_tests_total",
        }
        renamed.variable_name = renamed.variable_name.replace(var_rename)

        return (
            renamed[["dt", "fips", "variable_name", "value"]]
            .assign(vintage=pd.Timestamp.utcnow())
            .sort_values(["dt", "fips", "variable_name"])
        )

    def _get_stats(self):
        df = self.get_all_sheet_to_df(
            "colorado_covid19_daily_state_statistics_cumulative", 0, 3
        )

        renamed = df.rename(
            columns={
                "Date": "dt",
                "Cases": "cases_total",
                "Tested": "tests_total",
                "Deaths": "deaths_total",
                "DthCOVID19": "deaths_confirmed",
                # "Hosp": "hospitalizations_total"
            }
        )

        renamed.dt = self._convert_dt(renamed.dt)
        renamed["fips"] = self.state_fips
        melted = renamed[
            [
                "dt",
                "fips",
                "cases_total",
                "tests_total",
                "deaths_total",
                "deaths_confirmed",
            ]
        ].melt(id_vars=["fips", "dt"], var_name="variable_name")
        # Drop na values
        melted = melted.dropna(subset=["value"])
        melted.value = melted.value.astype(int)

        return melted.assign(vintage=pd.Timestamp.utcnow())
