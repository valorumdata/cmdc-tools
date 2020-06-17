import pandas as pd
import textwrap

from .. import InsertWithTempTable, DatasetBaseNoDate


BASEURL = "https://usafactsstatic.blob.core.windows.net/public/data/"


class USAFactsCases(InsertWithTempTable, DatasetBaseNoDate):
    """
    Downloads USA Fact case data

    Source: https://usafacts.org/visualizations/coronavirus-covid-19-spread-map
    """

    filename = "covid-19/covid_confirmed_usafacts.csv"
    variablename = "cases_total"
    table_name = "usafacts_covid"
    pk = "(vintage, dt, fips, variable_id)"
    data_type = "covid"
    source = "https://usafacts.org/issues/coronavirus/"
    has_fips = True

    def __init__(self):
        super(USAFactsCases, self).__init__()

    def _insert_query(self, df: pd.DataFrame, table_name: str, temp_name: str, pk: str):
        out = f"""
        INSERT INTO data.{table_name} (vintage, dt, fips, variable_id, value)
        SELECT tt.vintage, tt.dt, tt.fips, mv.id as variable_id, tt.value
        FROM {temp_name} tt
        LEFT JOIN meta.covid_variables mv ON tt.variable_name=mv.name
        ON CONFLICT {pk} DO UPDATE SET value = excluded.value;
        """

        return textwrap.dedent(out)

    def get(self):
        # Load data from site and move dates from column names to
        # a new variable
        df = pd.read_csv(BASEURL + self.filename)
        df = df.drop(["County Name", "State"], axis=1).melt(
            id_vars=["countyFIPS", "stateFIPS"], var_name="dt", value_name="value"
        )
        df["dt"] = pd.to_datetime(df["dt"])

        # Drop Wade Hampton Census Area (2270) since it was renamed to
        # Kusilvak and Kusilvak is already included in the data. Also
        # drop Grand Princess Cruise ship (6000)
        df = df.query("(countyFIPS != 2270) & (countyFIPS != 6000)")

        # We will report county and state level values -- This means
        # we will group by state fips and then sum... We will then
        # ignore unallocated cases
        df_county = (
            df.query("countyFIPS > 1000")
            .drop("stateFIPS", axis=1)
            .rename(columns={"countyFIPS": "fips"})
        )
        df_state = (
            df.groupby(["stateFIPS", "dt"])["value"]
            .sum()
            .reset_index()
            .rename(columns={"stateFIPS": "fips"})
        )

        # Stack dfs and then add variable name
        out = pd.concat([df_county, df_state], axis=0, ignore_index=True)
        out["vintage"] = pd.Timestamp.utcnow().normalize()
        out["variable_name"] = self.variablename

        return out


class USAFactsDeaths(USAFactsCases, DatasetBaseNoDate):
    """
    Downloads USA Facts death data

    Source: https://usafacts.org/visualizations/coronavirus-covid-19-spread-map
    """

    filename = "covid-19/covid_deaths_usafacts.csv"
    variablename = "deaths_total"
