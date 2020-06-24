import pandas as pd
import requests
import us

from ..base import CountyData
from ...base import DatasetBaseNoDate


class Tennessee(DatasetBaseNoDate, CountyData):
    source = "https://www.tn.gov/content/tn/health/cedep/ncov/data.html"
    has_fips = True
    state_fips = int(us.states.lookup("Tennessee").fips)

    def get(self):
        # Save file url and read data in
        url = (
            "https://www.tn.gov/content/dam/tn/health/documents/cedep/"
            "novel-coronavirus/datasets/Public-Dataset-Daily-Case-Info.XLSX"
        )
        df = pd.read_excel(url, parse_dates=["DATE"])

        # Rename columns, select subset, add fips
        # Unused variables include: "NEW_CASES", "NEW_CONFIRMED",
        # "NEW_PROBABLE", "NEW_DEATHS", "NEW_RECOVERED", "NEW_HOSP"...
        crename = {
            "DATE": "dt",
            "TOTAL_CONFIRMED": "cases_confirmed",
            "TOTAL_PROBABLE": "cases_suspected",
            "TOTAL_CASES": "cases_total",
            "TOTAL_DEATHS": "deaths_total",
            "TOTAL_RECOVERED": "recovered_total",
            "TOTAL_ACTIVE": "active_total",
            "POS_TESTS": "positive_tests_total",
            "NEG_TESTS": "negative_tests_total",
            "TOTAL_HOSP": "hospital_beds_in_use_covid",
        }
        df = df.rename(columns=crename).loc[:, crename.values()]
        df["fips"] = self.state_fips

        out = df.melt(
            id_vars=["dt", "fips"], var_name="variable_name", value_name="value"
        ).dropna()
        out["vintage"] = pd.Timestamp.utcnow().normalize()

        return out


class TennesseeCounties(DatasetBaseNoDate, CountyData):
    source = "https://www.tn.gov/content/tn/health/cedep/ncov/data.html"
    has_fips = False
    state_fips = int(us.states.lookup("Tennessee").fips)

    def get(self):
        # Create url to excel file and read data
        url = (
            "https://www.tn.gov/content/dam/tn/health/documents/cedep/"
            "novel-coronavirus/datasets/Public-Dataset-County-New.XLSX"
        )
        df = pd.read_excel(url, parse_dates=["DATE"])

        crename = {
            "DATE": "dt",
            "COUNTY": "county",
            "TOTAL_CONFIRMED": "cases_confirmed",
            "TOTAL_PROBABLE": "cases_suspected",
            "TOTAL_CASES": "cases_total",
            "TOTAL_DEATHS": "deaths_total",
            "NEG_TESTS": "negative_tests_total",
            "POS_TESTS": "positive_tests_total",
            "TOTAL_RECOVERED": "recovered_total",
            "TOTAL_ACTIVE": "active_total",
            "TOTAL_HOSPITALIZED": "hospital_beds_in_use_covid_total",
        }
        df = df.rename(columns=crename)

        # Reshape
        out = df.melt(
            id_vars=["dt", "county"], var_name="variable_name", value_name="value"
        ).dropna()
        out["vintage"] = pd.Timestamp.utcnow().normalize()

        return out
