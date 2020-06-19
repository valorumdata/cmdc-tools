import pandas as pd
import requests

from ...base import DatasetBaseNoDate
from ..base import ArcGIS


class Nebraska(DatasetBaseNoDate, ArcGIS):
    ARCGIS_ID = ""
    source = (
        "https://nebraska.maps.arcgis.com/apps/opsdashboard/"
        "index.html#/4213f719a45647bc873ffb58783ffef3"
    )
    state_fips = 31

    def __init__(self, params=None):

        if params is None:
            params = {
                "f": "json",
                "where": "1=1",
                "outFields": "*",
                "returnGeometry": "false",
            }
        super().__init__(params)

    def arcgis_query_url(self, service="Covid19_Update_service", sheet=0, srvid=1):
        # "https://gis.ne.gov/Agency/rest/services/Covid19_Update_service/MapServer/0/query?f=json&where=1%3D1&returnGeometry=false&outFields=*"
        out = (
            f"https://gis.ne.gov/Agency/rest/services/{service}/MapServer/{sheet}/query"
        )
        # https://gis.ne.gov/Agency/rest/services/{service}/MapServer/{sheet}/query
        return out

    def get(self):
        state = self.get_state()
        county = self.get_county()
        county["dt"] = state["dt"].iloc[0]

        return pd.concat([state, county], ignore_index=True, sort=True).assign(
            vintage=pd.Timestamp.utcnow().normalize()
        )

    def get_state(self):
        res = requests.get(self.arcgis_query_url(), params=self.params)

        # Parse into PD df
        df = pd.DataFrame.from_records(
            [x["attributes"] for x in res.json()["features"]]
        )
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
        keep["dt"] = keep["dt"].map(lambda x: pd.datetime.fromtimestamp(x / 1000))

        keep["fips"] = self.state_fips

        return keep.melt(["dt", "fips"], var_name="variable_name")

    def get_county(self):
        res = requests.get(
            self.arcgis_query_url(service="COVID19_County_Layer"), params=self.params
        )
        df = pd.DataFrame.from_records(
            [x["attributes"] for x in res.json()["features"]]
        )
        # Rename columns
        colmap = {
            "totalCountyPosFin": "positive_tests_total",
            "totalCountyNotDetFin": "negative_tests_total",
            "totalCountyDeathsFin": "deaths_confirmed",
            "COUNTYFP": "fips",
        }

        return (
            df.rename(columns=colmap)
            .loc[:, list(colmap.values())]
            .assign(fips=lambda x: x["fips"].astype(int) + self.state_fips * 1000)
            .melt(id_vars=["fips"], var_name="variable_name")
        )
