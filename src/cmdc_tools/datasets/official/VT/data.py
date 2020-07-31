import pandas as pd
import us

from ...base import DatasetBaseNoDate
from ..base import ArcGIS


class Vermont(DatasetBaseNoDate, ArcGIS):
    ARCGIS_ID = "BkFxaEFNwHqX3tAw"
    source = (
        "https://experience.arcgis.com/experience/" "85f43bd849e743cb957993a545d17170"
    )
    state_fips = int(us.states.lookup("Vermont").fips)
    has_fips = True

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

        # Convert to datetime -- Need to divide by 1000 to convert from ms
        hosp["fips"] = self.state_fips
        hosp["dt"] = hosp["dt"].map(lambda x: self._esri_ts_to_dt(x))

        hosp["hospital_beds_in_use_covid_total"] = hosp.eval(
            "hospital_beds_in_use_covid_confirmed + hospital_beds_in_use_covid_suspected"
        )

        keepers = [
            "dt",
            "fips",
            "hospital_beds_in_use_covid_confirmed",
            "hospital_beds_in_use_covid_suspected",
            "hospital_beds_in_use_covid_total",
        ]
        hosp = hosp.loc[:, keepers].melt(
            id_vars=["dt", "fips"], var_name="variable_name", value_name="value"
        )

        return hosp

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

        county["dt"] = county["dt"].map(lambda x: self._esri_ts_to_dt(x))
        out = county.loc[:, ["dt", "fips", "cases_confirmed", "deaths_total"]].melt(
            id_vars=["dt", "fips"], var_name="variable_name", value_name="value"
        )

        return out

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
        state["dt"] = state["dt"].map(lambda x: self._esri_ts_to_dt(x))
        state["fips"] = self.state_fips

        state_keep = [
            "dt",
            "fips",
            "cases_total",
            "deaths_total",
            "recovered_total",
        ]
        state = state.loc[:, state_keep]
        state = state.melt(
            id_vars=["dt", "fips"], var_name="variable_name", value_name="value"
        )

        return state
