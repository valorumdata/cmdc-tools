import pandas as pd
import requests

from ..base import ArcGIS


class Montana():
    def __init__(self, params=None):
        self.ARCGID_ID = "qnjIrwR8z5Izc0ij"

        if params is None:
            self.params = {
                "f": "json",
                "where": "1=1",
                "outFields": "*",
                "returnGeometry": "false",
            }

        super(ArcGIS, self).__init__(params=params)

    def get(self):
        res = requests.get(self.arcgis_query_url(service="COVID_Cases_Production_View", sheet=0, srvid=None), params=self.params)
            
        df = pd.DataFrame.from_records(
            [x['attributes'] for x in res.json()["features"]]
        )

    def get_hospitalization_stats(self):
        res = requests.get(self.arcgis_query_url(service="COVID_Cases_Production_View", sheet=2, srvid=None), params=self.params)
        
        df = pd.DataFrame.from_records(
            [x['attributes'] for x in res.json()["features"]]
        )

    def get_tests_stats(self):
         res = requests.get(self.arcgis_query_url(service="COVID_Cases_Production_View", sheet=1, srvid=None), params=self.params)
        
        df = pd.DataFrame.from_records(
            [x['attributes'] for x in res.json()["features"]]
        )
        
url = "https://services.arcgis.com/qnjIrwR8z5Izc0ij/ArcGIS/rest/services/COVID19_CASES/FeatureServer/0/query"
params =  {
    "f": "json",
    "where": "1=1",
    "outFields": "*",
    "returnGeometry": "false",
}

res = requests.get(url, params=params)

res.json()
df = pd.DataFrame.from_records(
    [x['attributes'] for x in res.json()["features"]]
)

keep = df.rename(columns={
    "NAME": "county",
    "LAST_UPDATE": "dt",
    "Total": "cases_total"
})
keep = keep[['dt', 'county', 'cases_total']]

keep["dt"] = keep["dt"].map(
    lambda x: pd.datetime.fromtimestamp(x/1000)
)

# ------------------------------------------------------------------------
hosp_url = "https://services.arcgis.com/qnjIrwR8z5Izc0ij/ArcGIS/rest/services/COVID_Cases_Production_View/FeatureServer/2/query"
hosp_res = requests.get(hosp_url, params)
hosp_df = pd.DataFrame.from_records(
    [x['attributes'] for x in hosp_res.json()["features"]]
)
hosp_df

keep_hosp = hosp_df.rename(columns={
    "Date_Reported_to_CDEpi": "dt",
    "County": "county",
})

keep_hosp = keep_hosp[['county' ,'dt', 'Outcome', 'Hospitalization']].groupby('county')
agged = keep_hosp


# total_num_hospitalizations = len(keep_hosp.loc[keep_hosp.Hospitalization == 'P']) + len(keep_hosp.loc[keep_hosp.Hospitalization == 'Y'])

hospital_beds_in_use_covid = len(keep_hosp.loc[keep_hosp.Hospitalization == 'Y'])

total_recovered = len(keep_hosp.loc[keep_hosp.Outcome == 'Recovered'])

deaths_total = len(keep_hosp.loc[keep_hosp.Outcome == 'Deceased'])

active_total = len(keep_hosp.loc[keep_hosp.Outcome == 'Active'])
# ----------------------------------------------------------------------------
test_url = "https://services.arcgis.com/qnjIrwR8z5Izc0ij/ArcGIS/rest/services/COVID_Cases_Production_View/FeatureServer/1/query"
test_res = requests.get(test_url, params)
test_df = pd.DataFrame.from_records(
    [x['attributes'] for x in test_res.json()["features"]]
)
test_df
