import pandas as pd
import requests

# from cmdc.datasets.official.arcgis import Arcgis

def url_for_name(name):
    return f"https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/{name}/MapServer/0?f=json"

def data_url(service_id):
    return f"https://opendata.arcgis.com/datasets/{service_id}_0.csv"

def df(name):
    res = requests.get(url_for_name(name))
    service_id = res.json()['serviceItemId']

    return pd.read_csv(data_url(service_id))


res = requests.get(url_for_name("Ky_Cnty_COVID19_Cases_WGS84WM"))
res.json()
service_id = res.json()['serviceItemId']

df = df("Ky_Cnty_COVID19_Cases_WGS84WM")
