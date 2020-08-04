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
        df = self.get_all_sheet_to_df("Covid19_Update_service", 0, "Agency")

        df["hospital_beds_in_use_any"] = df.beds_total - df.beds_avail
        df["icu_beds_in_use_any"] = df.icu_beds_total - df.icu_beds_avail
        df["ventilators_in_use_any"] = df.vent_equip_total - df.vent_equip_avail
        df["positive_tests_total"] = (
            df.pos_gender_male + df.pos_gender_female + df.pos_gender_unknown
        )
        df["recovered_total"] = (
            df.rec_gender_male + df.rec_gender_female + df.rec_gender_unknown
        )
        df["deaths_total"] = (
            df.dec_gender_male + df.dec_gender_female + df.dec_gender_unknown
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
        keep["dt"] = keep["dt"].map(lambda x: self._esri_ts_to_dt(x))

        keep["fips"] = self.state_fips

        return keep.melt(["dt", "fips"], var_name="variable_name")

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
                tests_total=lambda x: x.eval("positive_tests_total + negative_tests_total")
            )
            .melt(id_vars=["fips"], var_name="variable_name")
        )
