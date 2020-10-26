import pandas as pd
import us

from ... import DatasetBaseNoDate
from .. import CountyData


class NorthDakota(DatasetBaseNoDate, CountyData):
    start_date = "2020-04-29"
    source = "https://www.health.nd.gov/diseases-conditions/coronavirus/north-dakota-coronavirus-cases"
    state_fips = int(us.states.lookup("North Dakota").fips)
    has_fips = False
    url = "https://www.health.nd.gov/sites/www/files/documents/Files/MSS/coronavirus/charts-data/PublicUseData.csv"

    def get(self) -> pd.DataFrame:
        df = pd.read_csv(self.url, parse_dates=["Date"])
        columns = {
            "COUNTY": "county",
            "Date": "dt",
            "Total Deaths": "deaths_total",
            "Cases (Confirmed Only)": "cases_total",
            "Negative PCR tests (susceptible test encounters)": "negative_tests_total",
            "Active Hospitalized Cases": "hospital_beds_in_use_covid_total",
        }
        return (
            df.rename(columns=columns)
            .loc[:, list(columns.values())]
            .assign(
                vintage=self._retrieve_vintage(),
                positive_tests_total=lambda x: x["cases_total"],
            )
            .assign(tests_total=lambda x: x.eval("positive_tests_total + cases_total"))
            .melt(
                id_vars=["vintage", "dt", "county"],
                var_name="variable_name",
                value_name="value",
            )
            .assign(value=lambda x: x["value"].astype(int))
        )
