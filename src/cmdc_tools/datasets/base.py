import random
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
