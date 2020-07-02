import pandas as pd
import requests
import us

from ...base import DatasetBaseNoDate
from ..base import CountyData


class Delaware(DatasetBaseNoDate, CountyData):
    has_fips = False
    state_fips = int(us.states.lookup("Delaware").fips)
    source_map = {
        "Sussex": "https://myhealthycommunity.dhss.delaware.gov/locations/county-sussex/download_covid_19_data",
        "Kent": "https://myhealthycommunity.dhss.delaware.gov/locations/county-kent/download_covid_19_data",
        "New Castle": "https://myhealthycommunity.dhss.delaware.gov/locations/county-new-castle/download_covid_19_data",
    }
    source = list(source_map.values())

    def get(self):
        dfs = []
        for (county, url) in self.source_map.items():
            df = self._get_from_source(url)
            df["county"] = county
            dfs.append(df)

        df = pd.concat(dfs, ignore_index=True, sort=False)
        df["vintage"] = pd.Timestamp.utcnow().normalize()

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
            .rename(
                columns={
                    "Location": "county",
                    "Statistic": "variable_name",
                    "Value": "value",
                }
            )
            .loc[:, ["dt", "county", "variable_name", "value"]]
        )

        # Rename variables and drop any variables that we haven't renamed
        df["variable_name"] = df["variable_name"].replace(var_rename)
        df = df.query("variable_name in @var_rename.values()")
        df["value"] = df["value"].astype(int)

        return df
