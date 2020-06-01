import pandas as pd
import textwrap
import us

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
    table_name = "mobility_dex"
    geo_name = "state"
    pk = '(dt, fips, variable)'

    def _url(self):
        return self.__url.format(BASE=BASE_URL, geo=self.geo_name)

    def get(self):
        df = pd.read_csv(self._url(), parse_dates=["date"])

        df = df.melt(
            id_vars=["date", "state"],
            var_name="variable",
            value_name="value"
        ).rename(columns={"date": "dt"})

        df["fips"] = df["state"].map(
            lambda x: us.states.mapping("abbr", "fips")[x]
        ).astype(int)
        df = df.drop("state", axis="columns")

        return df[["dt", "fips", "variable", "value"]]

    def _insert_query(self, df, table_name, temp_name, pk):
        if not pk.startswith("("):
            pk = f"({pk})"

        out = f"""
        INSERT INTO data.{table_name} (dt, fips, variable, value)
        SELECT tt.dt, tt.fips, tt.variable, tt.value
        FROM {temp_name} tt
        ON CONFLICT {pk} DO NOTHING;
        """
        return textwrap.dedent(out)


class CountyDex(StateDex):
    pk = '(dt, fips, variable)'
    geo_name = "county"

    def get(self):
        df = pd.read_csv(self._url(), parse_dates=["date"])

        df = df.melt(
            id_vars=["date", "county"],
            var_name="variable",
            value_name="value"
        ).rename(columns={"date": "dt", "county": "fips"})

        return df[["dt", "fips", "variable", "value"]]
