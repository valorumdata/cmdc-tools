import random
from cmdc.datasets.db_util import TempTable
import sqlalchemy as sa


class DatasetBase:
    def __init__(self):
        pass

    def get(self):
        raise NotImplementedError("Must be implemented by subclass")

    def put(self, conn, df):
        raise NotImplementedError("Must be implemented by subclass")

    def put_prep(self, conn, df):
        pass


def _build_on_conflict_do_nothing_query(df, t_home, t_temp, pkey):
    colnames = ", ".join(list(df))
    cols = "(" + colnames + ")"
    if not pkey.startswith("("):
        pkey = f"({pkey})"

    return f"""
    INSERT INTO data.{t_home} {cols}
    SELECT {colnames} from {t_temp}
    ON CONFLICT {pkey} DO NOTHING;
    """


class OnConflictNothingBase(DatasetBase):
    def put(self, connstr, df=None):
        if df is None:
            if hasattr(self, "df"):
                df = self.df
            else:
                raise ValueError("No df found, please pass")

        if not hasattr(self, "pk"):
            msg = "field `pk` must be set on subclass of OnConflictNothingBase"
            raise ValueError(msg)

        temp_name = "__" + self.table_name + str(random.randint(1000, 9999))
        with sa.create_engine(connstr).connect() as conn:
            kw = dict(temp=False, if_exists="replace", destroy=True)
            with TempTable(df, temp_name, conn, **kw):
                sql = _build_on_conflict_do_nothing_query(
                    df, self.table_name, temp_name, self.pk
                )
                conn.execute(sql)
