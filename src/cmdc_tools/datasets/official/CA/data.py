import pandas as pd
import textwrap

import us

from ..base import CountyData
from ... import DatasetBaseNoDate


CA_COUNTY_URL = "https://data.chhs.ca.gov/"
CA_COUNTY_URL += "dataset/6882c390-b2d7-4b9a-aefa-2068cee63e47/resource/"
CA_COUNTY_URL += "6cd8d424-dfaa-4bdd-9410-a3d656e1176e/download/covid19data.csv"


class CACountyData(DatasetBaseNoDate, CountyData):
    source = "https://public.tableau.com/profile/ca.open.data#!/vizhome/COVID-19HospitalsDashboard/Hospitals"
    state_fips = int(us.states.lookup("California").fips)
    has_fips = False
    base_url = "https://data.ca.gov/dataset/"

    def get(self):
        cd_df = self.get_case_death_data()
        hosp_df = self.get_hospital_data()
        df = pd.concat([cd_df, hosp_df], axis=0, ignore_index=True)
        df["value"] = df["value"].astype(int)
        df["vintage"] = pd.Timestamp.utcnow().normalize()

        return df

    def get_case_death_data(self):
        url = self.base_url + "590188d5-8545-4c93-a9a0-e230f0db7290/resource/"
        url += "926fd08f-cc91-4828-af38-bd45de97f8c3/download/"
        url += "statewide_cases.csv"
        df = pd.read_csv(url, parse_dates=["date"])

        # Rename columns and subset data
        crename = {
            "date": "dt",
            "county": "county",
            "totalcountconfirmed": "cases_total",
            "totalcountdeaths": "deaths_total",
        }
        df = df.rename(columns=crename).loc[:, crename.values()]

        # Reshape
        out = df.melt(
            id_vars=["dt", "county"], var_name="variable_name", value_name="value"
        ).dropna()

        return out

    def get_hospital_data(self):
        # Get url for download
        url = self.base_url + "529ac907-6ba1-4cb7-9aae-8966fc96aeef/resource/"
        url += "42d33765-20fd-44b8-a978-b083b7542225/download/"
        url += "hospitals_by_county.csv"
        df = pd.read_csv(url, parse_dates=["todays_date"])

        # Rename columns and subset data
        crename = {
            "todays_date": "dt",
            "county": "county",
            "hospitalized_covid_confirmed_patients": "hospital_beds_in_use_covid_confirmed",
            "hospitalized_suspected_covid_patients": "hospital_beds_in_use_covid_suspected",
            "hospitalized_covid_patients": "hospital_beds_in_use_covid_total",
            "all_hospital_beds": "hospital_beds_capacity_count",
            "icu_covid_confirmed_patients": "icu_beds_in_use_covid_confirmed",
            "icu_suspected_covid_patients": "icu_beds_in_use_covid_suspected",
            # "icu_available_beds": "icu_beds_capacity_count", Unsure if this is capacity
        }
        df = df.rename(columns=crename).loc[:, crename.values()]
        df["icu_beds_in_use_covid_total"] = df.eval(
            "icu_beds_in_use_covid_confirmed + icu_beds_in_use_covid_suspected"
        )

        # Reshape
        out = df.melt(
            id_vars=["dt", "county"], var_name="variable_name", value_name="value"
        ).dropna()

        return out
