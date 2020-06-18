import pandas as pd

from ...base import DatasetBaseNoDate
from ..base import ArcGIS


class Vermont(DatasetBaseNoDate, ArcGIS):
    ARCGIS_ID = "BkFxaEFNwHqX3tAw"
    source = (
        "https://experience.arcgis.com/experience/" "85f43bd849e743cb957993a545d17170"
    )

    def _insert_query(self, df, table_name, temp_name, pk):
        out = f"""
        INSERT INTO data.{table_name} (vintage, dt, fips, variable_id, value)
        SELECT tt.vintage, tt.dt, us.fips, mv.id as variable_id, tt.value
        FROM {temp_name} tt
        INNER JOIN meta.us_fips us ON tt.fips=us.fips
        LEFT JOIN meta.covid_variables mv ON tt.variable_name=mv.name
        ON CONFLICT {pk} DO NOTHING
        """
        return out

    def get(self):
        # Download county data which only includes cases and deaths in VT
        county = self.get_all_sheet_to_df(service="VT_Counties_Cases", sheet=0, srvid=1)
        county = county.rename(
            columns={
                "CNTYGEOID": "fips",
                "Cases": "cases_total",
                "Deaths": "deaths_total",
                "DateUpd": "dt",
            }
        )

        # Convert Timestamps
        county["dt"] = pd.to_datetime(
            county["dt"].map(lambda x: pd.datetime.fromtimestamp(x / 1000).date())
        )
        county = county.loc[:, ["dt", "fips", "cases_total", "deaths_total"]]
        county = county.melt(
            id_vars=["dt", "fips"], var_name="variable_name", value_name="value"
        )

        state = self.get_all_sheet_to_df(service="county_summary", sheet=0, srvid=1)
        state = state.rename(
            columns={
                "date": "dt",
                # "positive_cases": "daily_positive_tests_total", # daily
                "cumulative_positives": "cases_total",
                "total_deaths": "deaths_total",  # cumulative
                "total_recovered": "recovered_total",  # cumulative
                # "daily_deaths": "deaths_total",
                # "daily_recovered": "daily_recovered_total", # daily
                "current_hospitalizations": "hospital_beds_in_use_covid_confirmed",  # daily
                "hosp_pui": "hospital_beds_in_use_covid_suspected",
            }
        )
        state["hospital_beds_in_use_covid_total"] = state.eval(
            "hospital_beds_in_use_covid_confirmed "
            + "+ hospital_beds_in_use_covid_confirmed"
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
            "hospital_beds_in_use_covid_confirmed",
            "hospital_beds_in_use_covid_suspected",
            "hospital_beds_in_use_covid_total",
        ]
        state = state.loc[:, state_keep]
        state = state.melt(
            id_vars=["dt", "fips"], var_name="variable_name", value_name="value"
        )

        result = (
            pd.concat([county, state], ignore_index=True)
            .assign(vintage=pd.Timestamp.utcnow().normalize())
            .dropna()
        )
        result["fips"] = result["fips"].astype(int)

        return result.sort_values(["dt", "fips"])
