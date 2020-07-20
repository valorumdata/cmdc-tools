import pandas as pd
import us

from ...base import DatasetBaseNoDate
from ..base import ArcGIS


def _convert_dt_col(df):
    df["dt"] = (
        pd.to_datetime(
            df["dt"].map(lambda x: pd.datetime.fromtimestamp(x / 1000).date())
        )
        .dt.tz_localize("US/Indiana-Starke")
        .dt.tz_convert("UTC")
        .dt.normalize()
    )


class MissouriFips(DatasetBaseNoDate, ArcGIS):
    ARCGIS_ID = "Bd4MACzvEukoZ9mR"
    state_fips = int(us.states.lookup("Missouri").fips)
    source = "http://mophep.maps.arcgis.com/apps/MapSeries/index.html?appid=8e01a5d8d8bd4b4f85add006f9e14a9d"
    has_fips = True

    @property
    def _vintage(self):
        return pd.Timestamp.utcnow().normalize()

    def get(self):
        df = self._get()
        df.value = df.value.astype(int)
        # Filter out fips==null
        # Drop county column
        return df.dropna(subset=["fips"]).drop("county", axis=1)

    def _get(self):
        cases = self._get_county_cases()
        hosp = self._get_hosp()
        county_deaths = self._get_county_deaths()
        state_deaths = self._get_deaths_timeseries()
        tests = self._get_tests()

        result = pd.concat(
            [cases, hosp, county_deaths, state_deaths, tests], sort=False
        )
        return result

    def _get_county_cases(self):
        df = self.get_all_sheet_to_df("Attack_Rate_Automated", 0, 6)
        renamed = df.rename(columns={"County": "county", "Cases": "cases_total"})

        renamed = renamed[["county", "cases_total"]]

        return renamed.melt(id_vars=["county"], var_name="variable_name").assign(
            dt=self._vintage, vintage=self._vintage
        )

    def _get_hosp(self):
        df = self.get_all_sheet_to_df("MHA_Hospitalizations_Automated", 0, 6)

        renamed = df.rename(
            columns={
                "FIPS": "fips",
                "collectiondate": "dt",
                "numc19hosppats": "hospital_beds_in_use_any",
                "numvent": "ventilators_capacity_count",
                "numventuse": "ventilators_in_use_any",
                "County": "county",
            }
        )
        _convert_dt_col(renamed)
        gbc = renamed[
            [
                "dt",
                "fips",
                "county",
                "hospital_beds_in_use_any",
                "ventilators_capacity_count",
                "ventilators_in_use_any",
            ]
        ].groupby(["dt", "fips"])

        agged = gbc.agg(
            {
                "county": lambda x: x.iloc[0],
                "hospital_beds_in_use_any": "sum",
                "ventilators_capacity_count": "sum",
                "ventilators_in_use_any": "sum",
            }
        ).reset_index()

        return (
            agged.sort_values(["dt", "fips"])
            .melt(id_vars=["dt", "fips", "county"], var_name="variable_name")
            .assign(vintage=self._vintage)
        )

    def _get_county_deaths(self):
        df = self.get_all_sheet_to_df("county_MOHSIS_map", 0, 6)
        renamed = df.rename(columns={"DEATHS": "deaths_total", "NAME": "county"})
        return (
            renamed[["county", "deaths_total"]]
            .melt(id_vars=["county"], var_name="variable_name")
            .assign(dt=self._vintage, vintage=self._vintage)
        )

    def _get_deaths_timeseries(self):
        df = self.get_all_sheet_to_df("Daily_Deaths_Automated", 0, 6)
        renamed = df.rename(
            columns={"Date_of_Death": "dt", "Cumulative_Cases": "deaths_total"}
        )
        _convert_dt_col(renamed)
        return (
            renamed[["dt", "deaths_total"]]
            .melt(id_vars=["dt"], var_name="variable_name")
            .assign(vintage=self._vintage, fips=self.state_fips)
        )

    def _get_tests(self):
        df = self.get_all_sheet_to_df("PCR_Test_by_Date_Automated", 0, 6)
        renamed = df.rename(
            columns={
                "test_date2": "dt",
                "Negative": "negative_tests_total",
                "Positive": "positive_tests_total",
                "Total": "tests_total",
            }
        )
        _convert_dt_col(renamed)
        cumulative = renamed.sort_values("dt").set_index("dt").cumsum().reset_index()

        return (
            cumulative[
                ["dt", "negative_tests_total", "positive_tests_total", "tests_total",]
            ]
            .melt(id_vars=["dt"], var_name="variable_name")
            .assign(fips=self.state_fips, vintage=self._vintage)
        )


class MissouriCounty(MissouriFips, DatasetBaseNoDate):
    has_fips = False
    state_fips = int(us.states.lookup("Missouri").fips)
    source = "http://mophep.maps.arcgis.com/apps/MapSeries/index.html?appid=8e01a5d8d8bd4b4f85add006f9e14a9d"

    def get(self):
        df = self._get()
        df.value = df.value.astype(int)
        # Filter out county==null
        # Drop fips column
        return df.dropna(subset=["county"]).drop("fips", axis=1)
