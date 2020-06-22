import pandas as pd
import textwrap

import us

from ..base import CountyData
from ... import DatasetBaseNoDate


CA_COUNTY_URL = "https://data.chhs.ca.gov/"
CA_COUNTY_URL += "dataset/6882c390-b2d7-4b9a-aefa-2068cee63e47/resource/"
CA_COUNTY_URL += "6cd8d424-dfaa-4bdd-9410-a3d656e1176e/download/covid19data.csv"

C_RENAMER = {
    "County Name": "county",
    "Most Recent Date": "dt",
    "Total Count Confirmed": "cases_total",
    "Total Count Deaths": "deaths_total",
    "COVID-19 Positive Patients": "hospital_beds_in_use_covid_confirmed",
    "Suspected COVID-19 Positive Patients": "hospital_beds_in_use_covid_suspected",
    "ICU COVID-19 Positive Patients": "icu_beds_in_use_covid_confirmed",
    "ICU COVID-19 Suspected Patients": "icu_beds_in_use_covid_suspected",
}


class CACountyData(DatasetBaseNoDate, CountyData):
    source = CA_COUNTY_URL
    state_fips = int(us.states.lookup("California").fips)
    has_fips = False

    def get(self):

        df = pd.read_csv(CA_COUNTY_URL)
        df = df.rename(columns=C_RENAMER).loc[:, list(C_RENAMER.values())]
        df["dt"] = pd.to_datetime(df["dt"])
        df["vintage"] = pd.datetime.today()

        # Create totals
        df["hospital_beds_in_use_covid_total"] = df.eval(
            "hospital_beds_in_use_covid_confirmed + hospital_beds_in_use_covid_suspected"
        )
        df["icu_beds_in_use_covid_total"] = df.eval(
            "icu_beds_in_use_covid_confirmed + icu_beds_in_use_covid_suspected"
        )

        df = df.melt(
            id_vars=["vintage", "dt", "county"],
            var_name="variable_name",
            value_name="value",
        )

        return df
