import os
import time

import pandas as pd
import us

from ...base import DatasetBaseNoDate
from ..base import ArcGIS


class RhodeIsland(ArcGIS, DatasetBaseNoDate):
    ARCGIS_ID = "dkWT1XL4nglP5MLP"
    state_fips = int(us.states.lookup("Rhode Island").fips)
    has_fips: bool = False

    def __init__(self, params=None):
        super().__init__(params=params)

    def get(self):
        df = self.get_all_sheet_to_df(service="COVID_Public_Map_TEST", sheet=2, srvid=1)

        df.Date = df.Date.fillna(int(time.time()))

        df.Date = pd.to_datetime(
            df.Date.map(lambda x: pd.datetime.fromtimestamp(x / 1000).date())
        )
        dir_path = os.path.dirname(os.path.realpath(__file__))
        counties = pd.read_csv(f"{dir_path}/RI_counties.csv")
        counties.city = counties.city.str.upper()
        cols = {
            "Count_of_COVID_19_Positive": "cases_confirmed",  # cumulativeff
            "Covid_Deaths": "deaths_confirmed",  # cumulative
            "Covid_ICU": "icu_beds_in_use_covid_confirmed",  # daily
            "Covid_Ventilator": "ventilators_in_use_covid_confirmed",
            "Total_Covid_Lab_Tests": "total_tests",  # cumulative
            "Negative_Covid_Lab_Tests": "negative_tests_total",  # cumulative
            "City_Town": "city",
            "Date": "dt",  # TODO: Dates are all 2020-04-07. wtf?
        }
        return df
        renamed = df.rename(columns=cols)

        renamed["positive_tests_total"] = (
            renamed.total_tests - renamed.negative_tests_total
        )
        keep_cols = list(cols.values())
        keep_cols.append("positive_tests_total")
        renamed = renamed[keep_cols]
        renamed.city = renamed.city.str.upper()
        # Join county name
        joined = renamed.set_index("city").join(counties.set_index("city"), how="left")
        return joined
        jgb = joined.reset_index().groupby("county")
        result = jgb.agg(
            {
                "cases_confirmed": "sum",
                "deaths_confirmed": "max",
                "icu_beds_in_use_covid_confirmed": "max",
                "ventilators_in_use_covid_confirmed": "max",
                "total_tests": "max",
                "negative_tests_total": "max",
                "dt": "max",
            }
        )
        return (
            result.reset_index()
            .melt(id_vars=["dt", "county"], var_name="variable_name")
            .assign(vintage=pd.Timestamp.utcnow().normalize())
        )
