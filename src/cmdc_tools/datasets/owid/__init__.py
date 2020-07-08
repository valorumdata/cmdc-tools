import random
from typing import List

import pandas as pd
import sqlalchemy as sa

from ..base import DatasetBaseNoDate
from ..db_util import TempTable

meta_columns = [
    "iso_code",
    "continent",
    "location",
    "population",
    "population_density",
    "median_age",
    "aged_65_older",
    "aged_70_older",
    "gdp_per_capita",
    "extreme_poverty",
    "cvd_death_rate",
    "diabetes_prevalence",
    "female_smokers",
    "male_smokers",
    "handwashing_facilities",
    "hospital_beds_per_thousand",
    "life_expectancy",
]


class OWID(DatasetBaseNoDate):
    source = "https://ourworldindata.org/coronavirus-data"

    def get(self):
        url = "https://covid.ourworldindata.org/data/owid-covid-data.csv"
        return (
            pd.read_csv(url, parse_dates=["date"])
                .rename(columns={"date": "dt"})
        )

    def _put_one(self, connstr: str, sub: pd.DataFrame, table_name: str, cols: List[str]):
        temp_name = f"__{table_name}" + str(random.randint(1000, 9999))
        sql = """
        INSERT INTO data.{table_name} ({cols})
        SELECT {cols} from {temp_name}
        on conflict (iso_code) do nothing;
        """.format(
            cols=",".join(cols),
            temp_name=temp_name,
            table_name=table_name
        )

        with sa.create_engine(connstr).connect() as conn:
            kw = dict(temp=False, if_exists="replace", destroy=True)
            with TempTable(sub, temp_name, conn, **kw):
                conn.execute(sql)

    def put(self, conn: str, df: pd.DataFrame):
        # first handle locations
        locations = (
            df.groupby("iso_code")
                .apply(lambda x: x.loc[:, meta_columns].iloc[0])
        )
        self._put_one(conn, locations, "owid_locations", meta_columns)

        # then handle data
        data_columns = list(set(list(df)) - set(meta_columns))
        data = df.loc[:, data_columns + ["iso_code"]]
        self._put_one(conn, data, "owid_covid", data_columns)
