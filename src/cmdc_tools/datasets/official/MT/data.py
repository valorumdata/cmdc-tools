import pandas as pd
import requests

from ...base import DatasetBaseNoDate
from ..base import ArcGIS


class Montana(ArcGIS, DatasetBaseNoDate):
    def __init__(self, params=None):
        self.ARCGIS_ID = "qnjIrwR8z5Izc0ij"

        if params is None:
            self.params = {
                "f": "json",
                "where": "1=1",
                "outFields": "*",
                "returnGeometry": "false",
            }

        super().__init__(params=params)

    def get(self):
        dt = pd.Timestamp.today().normalize()

        res = requests.get(
            self.arcgis_query_url(
                service="COVID_Cases_Production_View", sheet=2, srvid=""
            ),
            params=self.params,
        )

        main = pd.DataFrame.from_records(
            [x["attributes"] for x in res.json()["features"]]
        )
        # get cases
        case_outcome = self.get_cases(main)
        # get hospitalzation
        hbiuc = self.get_hospitalization_stats(main)        

        return(
            case_outcome
            # Join tables together
            .join(hbiuc)
            # Reset index
            .reset_index()
            # Melt
            .melt(id_vars=["County"], var_name="variable_name")
            # Normalize
            .assign(vintage=dt, dt=dt)
        )
        
    def get_cases(self, df):
    
        case_outcome = (
            df.groupby(["County", "Outcome"])["Sex"]
            .count()
            .unstack(level="Outcome")
            .fillna(0)
            .astype(int)
            .rename(columns={
                "Active":"active_total", 
                "Deceased":"deaths_total",
                "Recovered":"recovered_total"
            })
        )  

        return case_outcome

    def get_hospitalization_stats(self, df):
        hbiuc = (
            df.groupby(["County", "Hospitalization"])["Sex"]
            .count()
            .unstack(level="Hospitalization")
            .fillna(0)
            .astype(int)["Y"]
            .rename("hospital_beds_in_use_covid_total")  
        )
        return hbiuc
