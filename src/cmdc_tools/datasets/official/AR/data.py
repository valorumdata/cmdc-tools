import pandas as pd
import requests

from ..base import ArcGIS


class Arkansas(ArcGIS):
    ARCGIS_ID = "PwY9ZuZRDiI5nXUB"

    def __init__(self, params=None):

        if params is None:
            params = {
                "f": "json",
                "where": "1=1",
                "outFields": "*",
                "returnGeometry": "false",
            }

        super(Arkansas, self).__init__(params)

    def get(self):
        url = self.arcgis_query_url(
            service="ADH_COVID19_Positive_Test_Results", sheet=0, srvid=""
        )
        res = requests.get(url, params=self.params)

        df = pd.DataFrame.from_records(
            [x['attributes'] for x in res.json()["features"]]
        )

        # Filter columns
        keep = df.rename(columns={
            "county_nam": "county",
            "positive": "positive_tests_total",
            "negative": "negative_tests_total",
            "Recoveries": "recovered_total",
            "deaths": "deaths_total",
            "active_cases": "active_total",
        })

        keep = keep[[
           "county",
           "positive_tests_total",
           "negative_tests_total",
           "recovered_total",
           "deaths_total",
           "active_total",
        ]]

        return keep
