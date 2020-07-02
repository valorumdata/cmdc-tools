import pandas as pd
import requests
import textwrap

from .. import InsertWithTempTable, DatasetBaseNoDate


CURRENT_URL = "https://covidtracking.com/api/v1/states/current.json"
HISTORIC_URL = "https://covidtracking.com/api/v1/states/daily.json"


class CTP(InsertWithTempTable, DatasetBaseNoDate):
    """
    Used to insert data and variable names into the database specified
    by schema.sql
    """

    table_name = "ctp_covid"
    pk = '("vintage", "dt", "fips", "variable_id")'

    def __init__(self):
        super(CTP, self).__init__()

        self.crenamer = {
            "date": "dt",
            "fips": "fips",
            "death": "deaths_total",
            "positive": "positive_tests_total",
            "negative": "negative_tests_total",
            "hospitalizedCurrently": "hospital_beds_in_use_covid_total",
            "inIcuCurrently": "icu_beds_in_use_covid_total",
            "onVentilatorCurrently": "ventilators_in_use_covid_total",
        }

    def _insert_query(self, df: pd.DataFrame, table_name: str, temp_name: str, pk: str):
        out = f"""
        INSERT INTO data.{table_name} (vintage, dt, fips, variable_id, value)
        SELECT tt.vintage, tt.dt, tt.fips, mv.id as variable_id, tt.value
        FROM {temp_name} tt
        LEFT JOIN meta.covid_variables mv ON tt.variable_name=mv.name
        ON CONFLICT {pk} DO UPDATE SET value = excluded.value
        """

        return textwrap.dedent(out)

    def get(self):
        """
        Fetches the data for the variables provided in the `__init__`
        method from the specified ACS dataset

        Returns
        -------
        df : pd.DataFrame
            A DataFrame with a column for each variable requested and
            a column, `fips` which specifies the geographic information
        """
        # Download data and ingest into DataFrame
        req = requests.get(HISTORIC_URL)
        df = (
            pd.DataFrame.from_records(req.json())
            .rename(columns=self.crenamer)
            .loc[:, self.crenamer.values()]
        )

        # Convert things to the type needed for database
        df["vintage"] = pd.datetime.today()
        df["dt"] = pd.to_datetime(df["dt"].astype(str))
        df["fips"] = pd.to_numeric(df["fips"])

        df = df.melt(
            id_vars=["vintage", "dt", "fips"],
            var_name="variable_name",
            value_name="value",
        ).dropna()

        return df
