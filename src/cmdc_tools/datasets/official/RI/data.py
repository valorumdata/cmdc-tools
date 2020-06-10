import time

import pandas as pd

from ...base import DatasetBaseNoDate
from ..base import ArcGIS


class RhodeIsland(ArcGIS, DatasetBaseNoDate):
    ARCGIS_ID = "dkWT1XL4nglP5MLP"
    def __init__(self, params=None):
        super().__init__(params=params)

    def get(self):
        df = self.get_all_sheet_to_df(service="COVID_Public_Map_TEST", sheet=2, srvid=1)

        df.Date = df.Date.fillna(int(time.time()))
        
        df.Date = pd.to_datetime(df.Date.map(
            lambda x: pd.datetime.fromtimestamp(x/1000).date()
        ))

        renamed = df.rename(columns={
            "Count_of_COVID_19_Positive": "cases_confirmed",
            "Covid_Deaths": "deaths_confirmed",
            "Covid_ICU": "icu_beds_in_use_covid_confirmed",
            "Covid_Ventilator": "ventilators_in_use_covid_confirmed",
            "Total_Covid_Lab_Tests": "total_tests",
            "Negative_Covid_Lab_Tests": "negative_tests_total",
            "City_Town": "city",
            "Date": "dt", # TODO: Dates are all 2020-04-07. wtf?
        })

        renamed['positive_tests_total'] = renamed.total_tests - renamed.negative_tests_total

        renamed = renamed[[
            "dt",
            "city",
            "cases_confirmed",
            "deaths_confirmed",
            "icu_beds_in_use_covid_confirmed",
            "ventilators_in_use_covid_confirmed",
            "total_tests",
            "negative_tests_total",
            "positive_tests_total",
        ]]
        return renamed
        return (
            renamed
            .sort_values(["dt", "city"])
            .melt(id_vars=['dt', 'city'], var_name="variable_name")
            .assign(vintage=pd.Timestamp.now().normalize())
        )
