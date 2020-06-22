import pandas as pd
import us

from ...base import DatasetBaseNoDate
from ..base import ArcGIS


class Vermont(DatasetBaseNoDate, ArcGIS):
    ARCGIS_ID = "BkFxaEFNwHqX3tAw"
    source = (
        "https://experience.arcgis.com/experience/" "85f43bd849e743cb957993a545d17170"
    )
    state_fips: int = int(us.states.lookup("Vermont").fips)
    has_fips: bool = True

    def get(self):
        state = self._get_daily_count()
        hosp = self._get_hosp()
        county = self._get_county_daily()

        result = (
            pd.concat([county, state, hosp], ignore_index=True)
            .assign(vintage=pd.Timestamp.utcnow().normalize())
            .dropna()
        )
        result["fips"] = result["fips"].astype(int)

        return result.sort_values(["dt", "fips"]).query("fips != 99999")

    def _get_hosp(self):
        hosp = self.get_all_sheet_to_df("V_EMR_Hospitalization_PUBLIC", 0, 1)
        hosp = hosp.rename(
            columns={
                "date": "dt",
                "current_hospitalizations": "hospital_beds_in_use_covid_confirmed",  # daily
                "hosp_pui": "hospital_beds_in_use_covid_suspected",
            }
        )
        hosp["hospital_beds_in_use_covid_total"] = (
            hosp["hospital_beds_in_use_covid_confirmed"]
            + hosp["hospital_beds_in_use_covid_suspected"]
        )

        hosp["dt"] = pd.to_datetime(
            hosp["dt"].map(lambda x: pd.datetime.fromtimestamp(x / 1000).date())
        )
        hosp["fips"] = 50

        hosp = hosp[
            [
                "dt",
                "fips",
                "hospital_beds_in_use_covid_confirmed",
                "hospital_beds_in_use_covid_suspected",
                "hospital_beds_in_use_covid_total",
            ]
        ]

        return hosp.melt(
            id_vars=["dt", "fips"], var_name="variable_name", value_name="value"
        )

    def _get_county_daily(self):
        county = self.get_all_sheet_to_df(
            "V_EPI_CountyDailyCount_GEO_PUBLIC", sheet=0, srvid=1
        )
        county = county.rename(
            columns={
                "CNTYGEOID": "fips",
                "date": "dt",
                "C_Total": "cases_confirmed",
                "D_Total": "deaths_total",
            }
        )

        county["dt"] = pd.to_datetime(
            county["dt"].map(lambda x: pd.datetime.fromtimestamp(x / 1000).date())
        )

        return county[["dt", "fips", "cases_confirmed", "deaths_total"]].melt(
            id_vars=["dt", "fips"], var_name="variable_name", value_name="value"
        )

    def _get_daily_count(self):
        state = self.get_all_sheet_to_df(
            service="V_EPI_DailyCount_PUBLIC", sheet=0, srvid=1
        )
        state = state.rename(
            columns={
                "date": "dt",
                # "positive_cases": "daily_positive_tests_total", # daily
                "cumulative_positives": "cases_total",
                "total_deaths": "deaths_total",  # cumulative
                "total_recovered": "recovered_total",  # cumulative
                # "daily_deaths": "deaths_total",
                # "daily_recovered": "daily_recovered_total", # daily
            }
        )

        # Convert Timestamps
        state["dt"] = pd.to_datetime(
            state["dt"].map(lambda x: pd.datetime.fromtimestamp(x / 1000).date())
        )
        state["fips"] = 50

        state_keep = [
            "dt",
            "fips",
            "cases_total",
            "deaths_total",
            "recovered_total",
        ]
        state = state[state_keep]
        state = state.melt(
            id_vars=["dt", "fips"], var_name="variable_name", value_name="value"
        )

        return state
