import pandas as pd
import requests
import us

from ...base import DatasetBaseNoDate
from ..base import CountyData


class Delaware(DatasetBaseNoDate, CountyData):
    has_fips = True
    state_fips = int(us.states.lookup("Delaware").fips)
    source = "https://myhealthycommunity.dhss.delaware.gov/locations/state"
    data_url = "https://myhealthycommunity.dhss.delaware.gov/locations/state/download_covid_19_data"

    def get(self):
        df = self._get_from_source(self.data_url).drop("Location", axis=1)
        df["vintage"] = pd.Timestamp.utcnow().normalize()
        df["fips"] = self.state_fips

        return df

    def _get_from_source(self, source):
        # Read data and set date
        df = pd.read_csv(source)
        df["dt"] = pd.to_datetime(df[["Year", "Month", "Day"]])

        # Renamer for the variables that we want to keep
        var_rename = {
            "Deaths": "deaths_total",
            "Cumulative Number of Positive Cases": "cases_total",
            "Recovered": "recovered_total",
            "Cumulative Number of Confirmed Positive Cases": "positive_tests_total",
            "Tested Negative": "negative_tests_total",
            "Total Persons Tested": "tests_total",
        }

        # We restrict to only totals (i.e., 'people') and only keep a subset of columns
        df = (
            df.query("Unit == 'people'")
            .rename(columns={"Statistic": "variable_name", "Value": "value",})
            .loc[:, ["dt", "Location", "variable_name", "value"]]
        )

        # Rename variables and drop any variables that we haven't renamed
        df["variable_name"] = df["variable_name"].replace(var_rename)
        df = df.query("variable_name in @var_rename.values()")
        df["value"] = df["value"].astype(int)

        return df


class DelawareKent(DatasetBaseNoDate, Delaware):
    has_fips = False
    source = "https://myhealthycommunity.dhss.delaware.gov/locations/county-kent"
    data_url = "https://myhealthycommunity.dhss.delaware.gov/locations/county-kent/download_covid_19_data"

    def get(self):
        df = self._get_from_source(self.data_url)
        df["county"] = df["Location"].str.replace("County", "").str.strip()
        df = df.drop("Location", axis=1)

        df["vintage"] = pd.Timestamp.utcnow().normalize()

        return df


class DelawareNewCastle(DatasetBaseNoDate, DelawareKent):
    source = "https://myhealthycommunity.dhss.delaware.gov/locations/county-new-castle"
    data_url = "https://myhealthycommunity.dhss.delaware.gov/locations/county-new-castle/download_covid_19_data"


class DelawareSussex(DatasetBaseNoDate, DelawareKent):
    source = "https://myhealthycommunity.dhss.delaware.gov/locations/county-sussex"
    data_url = "https://myhealthycommunity.dhss.delaware.gov/locations/county-sussex/download_covid_19_data"
