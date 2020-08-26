import textwrap

import pandas as pd

from .. import DatasetBaseNeedsDate, DatasetBaseNoDate, InsertWithTempTable


class NYTimesState(InsertWithTempTable, DatasetBaseNoDate):
    table_name = "nyt_covid"
    pk = "(vintage, dt, fips, variable_id)"
    data_type = "covid"
    source = "https://github.com/nytimes/covid-19-data"
    url = "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv"
    has_fips = True
    geo = "state"

    def __init__(self):
        pass

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
        df = pd.read_csv(self.url, parse_dates=["date"])
        df["vintage"] = self._retrieve_vintage()

        # We do some extra reshaping so we can get 0 cases and 0 deaths
        # when there is missing data... See this issue on github:
        # https://github.com/nytimes/covid-19-data/issues/79
        df = (
            df.rename(
                columns={"date": "dt", "cases": "cases_total", "deaths": "deaths_total"}
            )
            .drop(self.geo, axis=1)
            .pipe(lambda x: x.loc[~x["fips"].isna(), :])
            .assign(fips=lambda x: x["fips"].astype(int))
            .set_index(["vintage", "dt", "fips"])
            .unstack(level="fips")
            .fillna(0.0)
            .stack(level="fips")
            .stack(level=0)
        )
        df.index = df.index.set_names("variable_name", level=-1)
        df.name = "value"

        return df.reset_index()


class NYTimesCounty(NYTimesState, DatasetBaseNoDate):
    geo = ["county", "state"]
    url = (
        "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv"
    )
