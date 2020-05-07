import textwrap
import pandas as pd
from cmdc.datasets import OnConflictNothingBase

BASE_URL = "https://raw.githubusercontent.com/COVIDExposureIndices/COVIDExposureIndices/master"


class DailyStateLex(OnConflictNothingBase):
    ds = "lex"
    geo_name = "state"
    __url = "{BASE_URL}/{ds}_data/{geo}_{ds}_{ymd}.csv"
    geo_prefix = "s"

    @property
    def table_name(self):
        return f"cex_{self.geo_name}_{self.ds}"

    @property
    def pk(self):
        return f'({self.geo_prefix}_today, {self.geo_prefix}_prev, "date")'

    def _url(self, date):
        ymd = pd.to_datetime(date).strftime("%Y-%m-%d")
        return self.__url.format(
            BASE_URL=BASE_URL, ymd=ymd, ds=self.ds, geo=self.geo_name
        )

    def get(self, date):
        dt = pd.to_datetime(date)
        _date = pd.to_datetime(dt.strftime("%Y-%m-%d"))
        df = pd.read_csv(self._url(date), index_col=[0])
        df.index.names = [f"{self.geo_prefix}_prev"]
        df.columns.names = [f"{self.geo_prefix}_today"]
        return df.stack().rename(self.ds).reset_index().assign(date=_date)

    def _insert_query(self, df, table_name, temp_name, pk):
        colnames = ", ".join(list(df))
        cols = "(" + colnames + ")"
        if not pk.startswith("("):
            pk = f"({pk})"
        return textwrap.dedent(
            f"""
        INSERT INTO data.{table_name} {cols}
        SELECT {colnames} from {temp_name}
        ON CONFLICT {pk} DO UPDATE SET {self.ds} = excluded.{self.ds};
        """
        )


class DailyCountyLex(DailyStateLex):
    geo_name = "county"
    geo_prefix = "c"

    def _url(self, date):
        return super()._url(date) + ".gz"


class DailyStateDex(DailyStateLex):
    ds = "dex"

