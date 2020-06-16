import pandas as pd
import textwrap

from ..base import CountyData
from ... import DatasetBaseNoDate


CA_COUNTY_URL = "https://data.chhs.ca.gov/"
CA_COUNTY_URL += "dataset/6882c390-b2d7-4b9a-aefa-2068cee63e47/resource/"
CA_COUNTY_URL += "6cd8d424-dfaa-4bdd-9410-a3d656e1176e/download/covid19data.csv"

C_RENAMER = {
    "County Name": "name",
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

    def _insert_query(self, df, table_name, temp_name, pk):
        out = f"""
        INSERT INTO data.{table_name} (vintage, dt, fips, variable_id, value)
        SELECT tt.vintage, tt.dt, us.fips, mv.id as variable_id, tt.value
        FROM {temp_name} tt
        LEFT JOIN meta.us_fips us ON tt.name=us.name
        LEFT JOIN meta.covid_variables mv ON tt.variable_name=mv.name
        WHERE us.fips > 6000 AND us.fips < 7000
        ON CONFLICT {pk} DO NOTHING
        """

        return textwrap.dedent(out)

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
            id_vars=["vintage", "dt", "name"],
            var_name="variable_name",
            value_name="value",
        )

        return df
