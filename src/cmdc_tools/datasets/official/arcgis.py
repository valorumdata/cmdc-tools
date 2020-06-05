import pandas as pd
import requests


class Arcgis():

    def __init__(self,resource_id, dashboard_name, server_id=None):
        super(Arcgis, self).__init__()
        self.url = f"https://services{server_id}.arcgis.com/{resource_id}/arcgis/rest/services/{dashboard_name}/FeatureServer/0?f=json"
    
    def df(self):
        res = requests.get(self.url)
        service_id = res.json()['serviceItemId']

        data_url = f"https://opendata.arcgis.com/datasets/{service_id}_0.csv"

        return pd.read_csv(data_url)
