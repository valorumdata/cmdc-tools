import random
from typing import Optional

from abc import ABC, abstractmethod

from .db_util import TempTable
import sqlalchemy as sa
import pandas as pd


class DatasetBase:
    autodag = True

    def __init__(self):
        pass

    @abstractmethod
    def put(self, conn, df):
        pass

    def put_prep(self, conn, df):
        pass

    def log_covid_source(
        self,
        connstr: sa.engine.Engine,
        df: pd.DataFrame,
        source: str,
        state_fips: Optional[int] = None,
    ):
        """
        Log the source of all variables in the DataFrame df

        :param conn: SQLAlchemy engine
        :param df: The DataFrame added to the data.us_covid table
        :param source: A string containing the source of the data
        :param state_fips: If `df` recognizes locations by name lookup
        from `county` column, the fips state code must be passed to
        disambiguate the location code for the observation
        :return:
        """
        # check for valid column names
        # first look for fips
        columns = list(df.columns)

        if "fips" in df:
            join_locs = "LEFT JOIN META.us_fips ff using(fips)"
            loc = "fips"
        elif "county" in df:
            if state_fips is None:
                msg = "Found county column, but state_fips not given. Must pass to correctly join"
                raise ValueError(msg)
            assert isinstance(state_fips, int)
            assert state_fips < 100
            fips_min = state_fips * 1000  # map from XX to XX000
            fips_max = fips_min + 999  # map from XX000 to XX999

            select = "SELECT name, fips from meta.us_fips where fips between {fips_min} and {fips_max}"
            join_locs = f"LEFT JOIN ({select}) ff on ff.name = tt.county"
            loc = "county"
        else:
            raise ValueError("Expected either `fips` or `county` in `df`")

        if "variable_name" in df:
            var = "variable_name"
            join_covid = (
                "LEFT JOIN meta.covid_variables mv on mv.name = tt.variable_name"
            )
        elif "variable_id" in df:
            var = "variable_id"
            join_covid = "LEFT JOIN meta.covid_variables mv on mv.id = tt.variable_id"
        else:
            raise ValueError("Expected either `variable_name` or `variable_id` in `df`")

        temp_table = "__covid_sources_{}".format(str(random.randint(1000, 9999)))
        sql = f"""
        INSERT INTO data.covid_sources(date_accessed, location, variable_id, source)
        SELECT tt.this_date, ff.fips, mv.id, tt.src
        from {temp_table} tt
        {join_locs}
        {join_covid}
        ON CONFLICT (date_accessed, location, variable_id) DO UPDATE set source=EXCLUDED.source
        """

        this_date = pd.Timestamp.utcnow().normalize()

        to_sql = (
            df[[loc, var]].drop_duplicates().assign(this_date=this_date, src=source)
        )

        with sa.create_engine(connstr).connect() as conn:
            kw = dict(temp=False, if_exists="replace", destroy=True)
            with TempTable(to_sql, temp_table, conn, **kw):
                conn.execute(sql)


class DatasetBaseNoDate(DatasetBase, ABC):
    get_needs_date = False

    @abstractmethod
    def get(self):
        raise NotImplementedError("Must be implemented by subclass")


class DatasetBaseNeedsDate(DatasetBase, ABC):
    get_needs_date = True

    @abstractmethod
    def get(self, date: str):
        raise NotImplementedError("Must be implemented by subclass")

    def transform_date(self, date: pd.Timestamp) -> pd.Timestamp:
        return date

    def quit_early(self, date: pd.Timestamp) -> bool:
        return False


def _build_on_conflict_do_nothing_query(
    df: pd.DataFrame, t_home: str, t_temp: str, pk: str
):
    colnames = ", ".join(list(df))
    cols = "(" + colnames + ")"
    if not pk.startswith("("):
        pk = f"({pk})"

    return f"""
    INSERT INTO data.{t_home} {cols}
    SELECT {colnames} from {t_temp}
    ON CONFLICT {pk} DO NOTHING;
    """


class InsertWithTempTable(DatasetBase, ABC):
    def _insert_query(self, df: pd.DataFrame, table_name: str, temp_name: str, pk: str):

        out = _build_on_conflict_do_nothing_query(df, table_name, temp_name, pk)
        return out

    def _put(self, connstr: str, df: pd.DataFrame, table_name: str, pk: str):
        temp_name = "__" + table_name + str(random.randint(1000, 9999))
        with sa.create_engine(connstr).connect() as conn:
            kw = dict(temp=False, if_exists="replace", destroy=True)
            with TempTable(df, temp_name, conn, **kw):
                sql = self._insert_query(df, table_name, temp_name, pk)
                conn.execute(sql)

    def put(self, connstr: str, df=None):
        if df is None:
            if hasattr(self, "df"):
                df = self.df
            else:
                raise ValueError("No df found, please pass")

        if not hasattr(self, "pk"):
            msg = "field `pk` must be set on subclass of OnConflictNothingBase"
            raise ValueError(msg)

        self._put(connstr, df, self.table_name, self.pk)
