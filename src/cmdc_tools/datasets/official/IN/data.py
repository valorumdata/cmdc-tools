import pandas as pd
import requests

from ...base import DatasetBaseNoDate


class Indiana(DatasetBaseNoDate):
    def get(self):
        url = "https://www.coronavirus.in.gov/map/covid-19-indiana-universal-report-current-public.json"

        res = requests.get(url)
        df = pd.DataFrame(res.json()["metrics"])

        renamed = df.rename(
            columns={
                "date": "dt",
                "district": "fips",
                "m2b_hospitalized_icu_occupied_covid": "icu_beds_in_use_covid_confirmed",
                "m2b_hospitalized_icu_supply": "icu_beds_capacity_count",
                "m2b_hospitalized_icu_occupied_non_covid": "icu_beds_in_use_any",
                "m2b_hospitalized_vent_occupied_covid": "ventilators_in_use_covid_confirmed",
                "m2b_hospitalized_vent_occupied_non_covid": "ventilators_in_use_any",
                "m2b_hospitalized_vent_supply": "ventilators_capacity_count",
            }
        )

        renamed["dt"] = pd.to_datetime(renamed["dt"])

        typed = renamed[
            [
                "dt",
                "fips",
                "district_type",
                "icu_beds_in_use_covid_confirmed",
                "icu_beds_capacity_count",
                "icu_beds_in_use_any",
                "ventilators_in_use_covid_confirmed",
                "ventilators_in_use_any",
                "ventilators_capacity_count",
            ]
        ].astype(
            {
                "icu_beds_in_use_covid_confirmed": int,
                "icu_beds_capacity_count": int,
                "icu_beds_in_use_any": int,
                "ventilators_in_use_covid_confirmed": int,
                "ventilators_in_use_any": int,
                "ventilators_capacity_count": int,
            }
        )
        # Set state-wide data fips code to Indiana's fips
        typed.loc[typed.district_type == "s", "fips"] = 18

        # Drop any district level rows
        typed = typed[typed.district_type != "d"]

        return typed[
            [
                "dt",
                "fips",
                "icu_beds_in_use_covid_confirmed",
                "icu_beds_capacity_count",
                "icu_beds_in_use_any",
                "ventilators_in_use_covid_confirmed",
                "ventilators_in_use_any",
                "ventilators_capacity_count",
            ]
        ].melt(id_vars=["dt", "fips"], var_name="variable_name")
