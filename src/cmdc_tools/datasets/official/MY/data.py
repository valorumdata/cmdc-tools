import pandas as pd
import requests

from ..base import ArcGIS


class Maryland(ArcGIS):

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
        return




url = "https://services.arcgis.com/njFNhDsUCentVYJW/arcgis/rest/services/MASTERCaseTracker/FeatureServer/0/query"
params = {
    "f": "json",
    "where": "1=1",
    "outFields": "*",
    "returnGeometry": "false",
}
res = requests.get(url, params=params)
df = pd.DataFrame.from_records(
    [x['attributes'] for x in res.json()["features"]]
)

df.head()
