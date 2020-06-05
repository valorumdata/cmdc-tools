import pandas as pd
import requests

from ..base import ArcGIS


class Arkansas(ArcGIS):
   def __init__(self, params=None):
      self.ARCGID_ID = "PwY9ZuZRDiI5nXUB"

      if params is None:
         self.params = {
            "f": "json",
            "where": "1=1",
            "outFields": "*",
            "returnGeometry": "false",
         }
         
      super(ArcGIS, self).__init__(params=params)

   def get(self):
      res = requests.get(self.arcgis_query_url(service="ADH_COVID19_State_Case_Metrics", sheet=0, srvid=None))

      df = pd.DataFrame.from_records(
         [x['attributes'] for x in res.json()["features"]]
      )

      # TODO: Filter columns
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
