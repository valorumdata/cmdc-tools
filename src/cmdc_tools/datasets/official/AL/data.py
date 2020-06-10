import pandas as pd
import requests

from ...base import DatasetBaseNoDate
from ..base import ArcGIS


class Alabama(ArcGIS, DatasetBaseNoDate):
    ARCGIS_ID = "4RQmZZ0yaZkGR1zy"
    def __init__(self, params=None):
        if params is None:
            params = {
                "f": "json",
                "where": "1=1",
                "outFields": "*",
                "returnGeometry": "false",
            }

        super().__init__(params=params)
    
    def arcgis_query_url(self, service="COVID19_ALCountiesData", sheet=1, srvid=1):
        # https://gis.jccal.org/arcgis/rest/services/OpenData/COVID19_ALCountiesData/MapServer/1/query
        out = f"https://gis.jccal.org/arcgis/rest/services/OpenData/{service}/MapServer/{sheet}/query"
        return out
    
    def other_query_url(self, service="HospitalizedPatientTemporal_READ_ONLY", sheet=1, srvid=7):
        out = f"https://services{srvid}.arcgis.com/{self.ARCGIS_ID}/arcgis/rest/services/{service}/FeatureServer/{sheet}/query"
        return out

    def get(self):
        url = self.arcgis_query_url()
        res = requests.get(url, params=self.params)

        df = pd.DataFrame.from_records(
            [x['attributes'] for x in res.json()["features"]]
        )
        # Rename columns
        renamed = df.rename(columns={
            "NAME": "county",
            "FIPS": "fips",
            "ConfirmedCases": "cases_confirmed",
            "Recovered": "recovered_total",
            "COVID_Deaths": "deaths_confirmed",
            "DateReported": "dt",
        })

        renamed['negative_tests_total'] = renamed.LabTestCount - renamed.cases_confirmed

        renamed = renamed[[
            "dt",
            "county",
            "fips",
            "cases_confirmed",
            "recovered_total",
            "deaths_confirmed",
            "negative_tests_total"
        ]]
        renamed["dt"] = renamed["dt"].map(
            lambda x: pd.datetime.fromtimestamp(x/1000).date()
        )
        renamed = (
            renamed
            .set_index(['dt', 'county'])
            .fillna(0)
            .astype(int)
            .reset_index()
            .sort_values(['dt','county'])
            .melt(
                id_vars=['dt', 'county', 'fips'],
                var_name="variabled_name",
                value_name="value"
            )
            .assign(
                vintage=pd.Timestamp.now().normalize()
            )
        )

        return renamed
