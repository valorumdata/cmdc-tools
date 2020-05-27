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
        out = f"""
        INSERT INTO data.{table_name} (dt, s_prev, s_today, lex)
        SELECT csl.date, sp.fips as s_prev, st.fips as s_today, csl.lex
        FROM {temp_name} csl
        LEFT JOIN meta.us_states sp ON sp.abbreviation = csl.s_prev
        LEFT JOIN meta.us_states st ON st.abbreviation = csl.s_today
        ON CONFLICT ("dt", s_prev, s_today) DO UPDATE SET lex = excluded.lex;
        """
        return textwrap.dedent(out)


class DailyCountyLex(DailyStateLex):
    geo_name = "county"
    geo_prefix = "c"

    def _url(self, date):
        return super()._url(date) + ".gz"

    def get(self, date):
        out = super().get(date)
        cols = ["c_prev", "c_today"]
        assert ~out[cols].isna().any().any()
        out[cols] = out[cols].astype(int)
        return out

    def _insert_query(self, df, table_name, temp_name, pk):
        out = f"""
        INSERT INTO data.{table_name} (dt, c_prev, c_today, lex)
        SELECT csl.date, fp.fips as c_prev, ft.fips as c_today, csl.lex
        FROM {temp_name} csl
        LEFT JOIN meta.us_fips fp ON fp.fips = csl.c_prev
        LEFT JOIN meta.us_fips ft ON ft.fips = csl.c_today
        ON CONFLICT ("dt", c_prev, c_today) DO UPDATE SET lex = excluded.lex
        """
        return textwrap.dedent(out)


class StateDex(OnConflictNothingBase):
    __url = "{BASE}/dex_data/{geo}_dex.csv"
    table_name = "cex_state_dex"
    geo_name = "state"
    pk = '("dt", state)'
    first_select_col = "f.fips"
    join_on = "f.abbreviation = tt.state"

    def _url(self):
        return self.__url.format(BASE=BASE_URL, geo=self.geo_name)

    def get(self):
        df = pd.read_csv(self._url(), parse_dates=["date"])
        return df

    def _insert_query(self, df, table_name, temp_name, pk):
        cols = list(df)
        cols[cols.index("date")] = "dt"
        final_cols = "(" + ", ".join(cols) + ")"
        temp_cols = ", ".join([self.first_select_col] + list(df)[1:])
        if not pk.startswith("("):
            pk = f"({pk})"
        out = f"""
        INSERT INTO data.{table_name} {final_cols}
        SELECT {temp_cols} from {temp_name} tt
        LEFT JOIN meta.us_states f on {self.join_on}
        ON CONFLICT {pk} DO NOTHING;
        """
        return textwrap.dedent(out)


class CountyDex(StateDex):
    table_name = "cex_county_dex"
    pk = '("dt", county)'
    geo_name = "county"
    first_select_col = "f.fips"
    join_on = "tt.county = f.fips"

    def _insert_query(self, df, table_name, temp_name, pk):
        cols = list(df)
        cols[cols.index("date")] = "dt"
        final_cols = "(" + ", ".join(cols) + ")"
        temp_cols = ", ".join([self.first_select_col] + list(df)[1:])
        if not pk.startswith("("):
            pk = f"({pk})"
        out = f"""
        INSERT INTO data.{table_name} {final_cols}
        SELECT {temp_cols} from {temp_name} tt
        LEFT JOIN meta.us_fips f on {self.join_on}
        ON CONFLICT {pk} DO NOTHING;
        """
        return textwrap.dedent(out)
