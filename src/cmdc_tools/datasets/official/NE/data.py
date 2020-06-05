import pandas as pd
import requests

from ..base import ArcGIS


class Nebraska(ArcGIS):
    ARCGIS_ID = ""

    def __init__(self, params=None):

        if params is None:
            self.params = {
                "f": "json",
                "where": "1=1",
                "outFields": "*",
                "returnGeometry": "false",
            }
        super(ArcGIS, self).__init__(params=params)

    def arcgis_query_url(self, service="Covid19_Update_service", sheet=0, srvid=1):
        # "https://gis.ne.gov/Agency/rest/services/Covid19_Update_service/MapServer/0/query?f=json&where=1%3D1&returnGeometry=false&outFields=*"
        out = f"https://gis.ne.gov/Agency/rest/services/{service}/MapServer/{sheet}/query"

        return out

    def get(self):
        res = requests.get(self.arcgis_query_url(), params=self.params)        

        # Parse into PD df
        df = pd.DataFrame.from_records(
            [x['attributes'] for x in res.json()["features"]]
        )
        df['hospital_beds_in_use_any'] = df.beds_total - df.beds_avail
        df['icu_beds_in_use_any'] = df.icu_beds_total - df.icu_beds_avail
        df["ventilators_in_use_any"] = df.vent_equip_total - df.vent_equip_avail
        df["positive_tests_total"] = df.pos_gender_male + df.pos_gender_female + df.pos_gender_unknown
        df['recovered_total'] = df.rec_gender_male + df.rec_gender_female + df.rec_gender_unknown
        df['deaths_total'] = df.dec_gender_male + df.dec_gender_female + df.dec_gender_unknown

        # Rename columns using /schemas/covid_data.sql
        keep = df.rename(columns={
            'beds_total': "hospital_beds_capacity_count",
            'icu_beds_total': "icu_beds_capacity_count",
            'vent_equip_total': "ventilators_capacity_count",
            'rec_latest_pat_count': "recovered_total",
            'dash_update_date': "dt",
        })

        keep = keep[[
            'hospital_beds_in_use_any',
            'icu_beds_in_use_any',
            'recovered_total',
            'deaths_total',
            "ventilators_in_use_any",
            "positive_tests_total",
            "hospital_beds_capacity_count",
            "icu_beds_capacity_count",
            "ventilators_capacity_count",
            "recovered_total",
            "dt",
        ]]

        # TODO: Convert timestamps
        keep["dt"] = keep["dt"].map(
            lambda x: pd.datetime.fromtimestamp(x/1000)
        )

        return keep

    def get_county(self):
        res = requests.get(self.arcgis_query_url(service='COVID19_County_Layer'))
        df = pd.DataFrame.from_records(
            [x['attributes'] for x in res.json()["features"]]
        )

        # Rename columns
        keep = df.rename(columns={
            "NAME": "county",
            "totalCountyPosFin": "positive_tests_total",
            "totalCountyNotDetFin": "negative_tests_total",
            "totalCountyDeathsFin": "deaths_confirmed",
            "totalCountyDeaths": "deaths_suspected"
        })[['county', 'positive_tests_total', 'negative_tests_total', 'deaths_confirmed', 'deaths_suspected']]

        return keep
