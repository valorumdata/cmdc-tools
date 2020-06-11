import pandas as pd

from ...base import DatasetBaseNoDate
from ..base import ArcGIS


class SouthCarolina(ArcGIS, DatasetBaseNoDate):
    ARCGIS_ID = "XZg2efAbaieYAXmu"

    def get(self):
        df = self.get_all_sheet_to_df(service="COVID19", sheet=0, srvid=2)

        renamed = df.rename(columns={
            "NAME": "county",
            "Areakey": "fips",
            "Confirmed": "cases_confirmed",
            "Recovered": "recovered_total",
            "Death" : "deaths_total",
            "Date": "dt"
        })
        return df
