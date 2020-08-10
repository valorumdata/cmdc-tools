import pandas as pd
import requests
import us

from ...base import DatasetBaseNoDate
from ..base import ArcGIS


class Nebraska(DatasetBaseNoDate, ArcGIS):
    ARCGIS_ID = ""
    source = (
        "https://nebraska.maps.arcgis.com/apps/opsdashboard/"
        "index.html#/4213f719a45647bc873ffb58783ffef3"
    )
    state_fips = int(us.states.lookup("Nebraska").fips)
    has_fips = True

    def arcgis_query_url(
        self, service="Covid19_Update_service", sheet=0, srvid="Agency"
    ):
        out = f"https://gis.ne.gov/{srvid}/rest/services/{service}/MapServer/{sheet}/query"

        return out

    def get(self):
        state = self.get_state()
        county = self.get_county()
        county["dt"] = state["dt"].iloc[0]

        return (
            pd.concat([state, county], ignore_index=True, sort=True)
            .assign(vintage=self._retrieve_vintage())
            .drop_duplicates(subset=["dt", "vintage", "fips", "variable_name"])
        )

    def get_state(self):
        df = self.get_all_sheet_to_df("CovidUpdatePublic", 0, "enterprise")

        df["hospital_beds_in_use_any"] = df.eval("beds_total - beds_avail")
        df["icu_beds_in_use_any"] = df.eval("icu_beds_total - icu_beds_avail")
        df["ventilators_in_use_any"] = df.eval("vent_equip_total - vent_equip_avail")
        df["positive_tests_total"] = df.eval(
            "pos_gender_male + pos_gender_female + pos_gender_unknown"
        )
        df["recovered_total"] = df.eval(
            "rec_gender_male + rec_gender_female + rec_gender_unknown"
        )
        df["deaths_total"] = df.eval(
            "dec_gender_male + dec_gender_female + dec_gender_unknown"
        )

        # Rename columns using /schemas/covid_data.sql
        keep = df.rename(
            columns={
                "beds_total": "hospital_beds_capacity_count",
                "icu_beds_total": "icu_beds_capacity_count",
                "vent_equip_total": "ventilators_capacity_count",
                "rec_latest_pat_count": "recovered_total",
                "dash_update_date": "dt",
            }
        )

        keep = keep[
            [
                "hospital_beds_in_use_any",
                "icu_beds_in_use_any",
                "recovered_total",
                "deaths_total",
                "ventilators_in_use_any",
                "positive_tests_total",
                "hospital_beds_capacity_count",
                "icu_beds_capacity_count",
                "ventilators_capacity_count",
                "recovered_total",
                "dt",
            ]
        ]

        # Convert timestamps
        keep["dt"] = keep["dt"].map(lambda x: ne._esri_ts_to_dt(x))
        keep["fips"] = ne.state_fips

        out = keep.melt(id_vars=["dt", "fips"], var_name="variable_name")

        return out

    def get_county(self):
        df = self.get_all_sheet_to_df("Covid19MapV5", 0, "enterprise")

        # Rename columns
        colmap = {
            "totalCountyPosFin": "positive_tests_total",
            "totalCountyNotDetFin": "negative_tests_total",
            "totalCountyDeathsFin": "deaths_total",
            "COUNTYFP": "fips",
        }

        return (
            df.rename(columns=colmap)
            .loc[:, list(colmap.values())]
            .assign(
                fips=lambda x: x["fips"].astype(int) + self.state_fips * 1000,
                tests_total=lambda x: x.eval(
                    "positive_tests_total + negative_tests_total"
                ),
            )
            .melt(id_vars=["fips"], var_name="variable_name")
        )
