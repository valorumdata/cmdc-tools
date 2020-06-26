import pandas as pd
import textwrap
import us

from .. import InsertWithTempTable, DatasetBaseNeedsDate, DatasetBaseNoDate

BASE_URL = (
    "https://raw.githubusercontent.com/COVIDExposureIndices/COVIDExposureIndices/master"
)


class DailyStateLex(InsertWithTempTable, DatasetBaseNeedsDate):
    ds = "lex"
    geo_name = "state"
    __url = "{BASE_URL}/{ds}_data/{geo}_{ds}_{ymd}.csv"
    table_name = "mobility_lex"
    pk = '("dt", "fips_prev", "fips_today")'

    def _url(self, date: str):
        ymd = pd.to_datetime(date).strftime("%Y-%m-%d")

        return self.__url.format(
            BASE_URL=BASE_URL, ymd=ymd, ds=self.ds, geo=self.geo_name
        )

    def _make_fips(self, df: pd.DataFrame):
        states = us.states.mapping("abbr", "fips")
        out = df.copy()
        for col in ["fips_prev", "fips_today"]:
            out[col] = out[col].replace(states).astype(int)
        return out

    def get(self, date: str):
        dt = pd.to_datetime(date)
        _date = pd.to_datetime(dt.strftime("%Y-%m-%d"))
        df = pd.read_csv(self._url(date), index_col=[0])
        df.index.names = ["fips_prev"]
        df.columns.names = ["fips_today"]
        long = df.stack().rename(self.ds).reset_index().assign(date=_date)
        out = self._make_fips(long)

        for c in ["fips_prev", "fips_today"]:
            out[c] = out[c].astype(int)
        return out

    def _insert_query(self, df: pd.DataFrame, table_name: str, temp_name: str, pk: str):
        out = f"""
        INSERT INTO data.{table_name} (dt, fips_prev, fips_today, lex)
        SELECT date, fips_prev, fips_today, lex
        FROM {temp_name}
        ON CONFLICT ("dt", fips_prev, fips_today) DO UPDATE SET lex = excluded.lex;
        """
        return textwrap.dedent(out)

    def transform_date(self, date: pd.Timestamp) -> pd.Timestamp:
        return date - pd.Timedelta(days=6)

    def quit_early(self, date):
        return date.dayofweek >= 5


class DailyCountyLex(DailyStateLex, DatasetBaseNeedsDate):
    geo_name = "county"
    geo_prefix = "c"

    def _url(self, date: str):
        return super()._url(date) + ".gz"

    def _make_fips(self, df: pd.DataFrame):
        return df


class StateDex(InsertWithTempTable, DatasetBaseNoDate):
    __url = "{BASE}/dex_data/{geo}_dex.csv"
    table_name = "mobility_dex"
    geo_name = "state"
    pk = "(dt, fips, variable_id)"
    variables = ["dex", "num_devices", "dex_a", "num_devices_a"]

    def _url(self):
        return self.__url.format(BASE=BASE_URL, geo=self.geo_name)

    def _make_fips(self, df: pd.DataFrame):
        df["fips"] = df["state"].replace(us.states.mapping("abbr", "fips")).astype(int)
        return df.drop("state", axis="columns")

    def get(self):
        df = pd.read_csv(self._url(), parse_dates=["date"])
        id_vars = ["date", self.geo_name]

        df = (
            df[id_vars + self.variables]
            .melt(id_vars=id_vars, var_name="variable_name", value_name="value")
            .rename(columns={"date": "dt"})
        )

        df = self._make_fips(df)

        return df[["dt", "fips", "variable_name", "value"]]

    def _insert_query(self, df: pd.DataFrame, table_name: str, temp_name: str, pk: str):
        if not pk.startswith("("):
            pk = f"({pk})"

        out = f"""
        INSERT INTO data.{table_name} (dt, fips, variable_id, value)
        SELECT tt.dt, tt.fips, mdv.id as variable_id, tt.value
        FROM {temp_name} tt
        LEFT JOIN meta.mobility_dex_variables mdv using (variable_name)
        ON CONFLICT {pk} DO NOTHING;
        """
        return textwrap.dedent(out)


class CountyDex(StateDex, DatasetBaseNoDate):
    geo_name = "county"

    def _make_fips(self, df: pd.DataFrame):
        return df.rename(columns=dict(county="fips"))
