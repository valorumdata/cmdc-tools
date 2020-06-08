import pandas as pd
import textwrap

from .. import InsertWithTempTable, DatasetBaseNeedsDate, DatasetBaseNoDate


class NYTimesState(InsertWithTempTable, DatasetBaseNoDate):
    table_name = "covid_nytimes"
    pk = '(vintage, dt, fips, variable_id)'
    url = "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv"

    def __init__(self):
        pass

    def _insert_query(self, df: pd.DataFrame, table_name: str, temp_name: str, pk: str):
        out = f"""
        INSERT INTO data.{table_name} (vintage, dt, fips, variable_id, value)
        SELECT tt.vintage, tt.dt, tt.fips, mv.id as variable_id, tt.value
        FROM {temp_name} tt
        LEFT JOIN meta.covid_variables mv ON tt.variable_name=mv.name
        ON CONFLICT {pk} DO NOTHING
        """

        return textwrap.dedent(out)

    def get(self):
        df = pd.read_csv(self.url, parse_dates=["date"])
        df["vintage"] = pd.datetime.today().date()

        # We do some extra reshaping so we can get 0 cases and 0 deaths
        # when there is missing data... See this issue on github:
        # https://github.com/nytimes/covid-19-data/issues/79
        df = df.rename(
            columns={
                "date": "dt",
                "cases": "cases_total",
                "deaths": "deaths_total"
            }
        ).drop("state", axis=1).set_index(
            ["vintage", "dt", "fips"]
        ).unstack(level="fips").fillna(0.0).stack(
            level="fips"
        ).stack(
            level=0
        )
        df.index = df.index.set_names("variable_name", level=-1)
        df.name = "value"

        return df.reset_index()



