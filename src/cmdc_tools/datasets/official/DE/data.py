import pandas as pd
import requests
import us

from ...base import DatasetBaseNoDate
from ..base import CountyData


class Delaware(DatasetBaseNoDate, CountyData):
    state_fips = int(us.states.lookup("Delaware").fips)
    has_fips: bool = False
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

        return pd.concat(dfs, sort=False).melt(
            id_vars=["dt", "county"], var_name="variable_name"
        )

    def _get_from_source(self, source):
        df = pd.read_csv(source)

        df["dt"] = pd.to_datetime(df[["Year", "Month", "Day"]])
        keep = df.loc[df.Unit == "people"][
            ["Location", "County", "dt", "Statistic", "Value"]
        ]
        pivoted = (
            keep.set_index(["Location", "County", "dt"])
            .pivot(columns="Statistic")["Value"]
            .reset_index()
        )
        renamed = pivoted.rename(
            columns={
                "County": "county",
                "Confirmed Deaths": "deaths_confirmed",
                "Cumulative Number of Confirmed Positive Cases": "cases_confirmed",
                # 'Cumulative Number of Positive Cases': "cases_suspected",
                "Deaths": "deaths_total",
                "Cumulative Number of Probable Positive Cases": "cases_suspected",
                "Recovered": "recovered_total",
                "Tested Negative": "negative_tests_total",
                "Total Persons Tested": "tests_total",
            }
        )

        return renamed[
            [
                "dt",
                "deaths_confirmed",
                "cases_confirmed",
                "cases_suspected",
                "deaths_total",
                "cases_suspected",
                "recovered_total",
                "negative_tests_total",
                "tests_total",
            ]
        ]

    # def _get_sussex_county(self):
    #     df = self._get_from_source(self.source_map["sussex"])
    #     df["county"] = "Sussex"
    #     return df

    # def _get_kent_county(self):
    #     df = self._get_from_source(self.source_map["kent"])
    #     df["county"] = "Kent"
    #     return df

    # def _get_new_castle_county(self):
    #     df = self._get_from_source(self.source_map["new castle"])
    #     df["county"] = "New Castle"
    #     return df
