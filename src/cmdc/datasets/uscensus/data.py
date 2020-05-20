import io
import json
import pandas as pd
import random
import requests
import sqlalchemy as sa

from cmdc.datasets.uscensus.census import ACSAPI
from cmdc.datasets.base import OnConflictNothingBase
from cmdc.datasets.db_util import TempTable


class ACS(ACSAPI, OnConflictNothingBase):
    """
    Used to insert data and variable names into the database specified
    by schema.sql
    """
    data_table = "acs_data"
    data_pk = '("id", "fips")'
    variable_table = "acs_variables"
    variable_pk = '("id")'

    def __init__(self, cols, geo, product, table, year, key):
        super(ACS, self).__init__(
            product=product, table=table, year=year, key=key
        )
        self.cols = cols
        self.geo = geo

    def _create_fips(self, df):
        """
        Converts geographic columns into a fips code

        Parameters
        ----------
        df : pd.DataFrame
            The output of a `data_get` request and must include the
            relevant geographic columns

        Returns
        -------
        df : pd.DataFrame
            A DataFrame with the fips code values included and the
            other geographic columns dropped
        """
        if self.geo == "state":
            df["fips"] = df["state"].astype(int)
            df = df.drop(columns=["state"])
        elif self.geo == "county":
            df["fips"] = df["state"].astype(int)*1_000 + df["county"].astype(int)
            df = df.drop(columns=["state", "county"])
        elif self.geo == "tract":
            df["fips"] = (
                df["state"].astype(int)*1_000_000_000 +
                df["county"].astype(int)*1_000_000 +
                df["tract"].astype(int)
            )
            df = df.drop(columns=["state", "county", "tract"])
        else:
            raise ValueError("Only state/county/tract are supported")

        return df

    def _data_insert_query(self, df, table_name, temp_name, pk):
        _sql_data_insert = f"""
        INSERT INTO uscensus.{table_name} (id, fips, value)
        SELECT vt.id, tt.fips, tt.value FROM {temp_name} tt
        LEFT JOIN uscensus.{self.variable_table} vt
          ON vt.census_id=tt.census_id AND
            vt.year={self.year} AND
            vt.product='{self.product}'
        ON CONFLICT {pk} DO UPDATE set value = excluded.value;
        """

        return _sql_data_insert

    def data_get(self):
        """
        Fetches the data for the variables provided in the `__init__`
        method from the specified ACS dataset

        Returns
        -------
        df : pd.DataFrame
            A DataFrame with a column for each variable requested and
            a column, `fips` which specifies the geographic information
        """
        # Fetch data
        df = super(ACS, self).get(self.cols, self.geo)

        # Convert to fips representation
        df = self._create_fips(df)

        # Reshape into desired format
        df = df.melt(id_vars="fips", var_name="census_id", value_name="value")

        return df

    def _var_insert_query(self, df, table_name, temp_name, pk):
        _sql_var_insert = f"""
        INSERT INTO uscensus.{table_name} (year, product, census_id, label)
        SELECT year, product, census_id, label FROM {temp_name}
        ON CONFLICT (year, product, census_id) DO NOTHING;
        """

        return _sql_var_insert

    def variable_get(self):
        """
        Fetches the variables for the specified ACS dataset

        Returns
        -------
        all_variables : pd.DataFrame
            A DataFrame with columns (year, product, census_id, label)
            which matches the columsn in the `uscensus.acs_variables`
            table
        """
        # Fetch variables json
        variable_json = json.loads(
            requests.get(self.dataset["c_variablesLink"]).text
        )

        # Load into DataFrame
        all_variables = pd.DataFrame.from_dict(
            variable_json["variables"]
        ).T

        # Only keep 'Estimate' variables
        is_variable = all_variables["label"].str.contains("Estimate")
        all_variables = all_variables.loc[is_variable, ["label"]].reset_index()

        all_variables["year"] = self.dataset["c_vintage"]
        all_variables["product"] = self.product
        all_variables = all_variables.rename(columns={"index": "census_id"})

        return all_variables

    def _put(self, connstr, table="variable", df=None):
        """
        Inserts the variable data into the `uscensus.acs_variables`
        table

        Parameters
        ----------
        connstr : string
            A postgres connection string that can be used by sqlalchemy
        d_or_v : string
            A string that denotes whether we're putting data or
            variables into the database
        df : pd.DataFrame
            The DataFrame with all of the variables contained in a
            particular data product
        """
        if df is None:
            if table == "data":
                df = self.data_get()
            elif table == "variable":
                df = self.variable_get()

        if table == "data":
            tablename = self.data_table
            pk = self.data_pk
            _insert_cmd = self._data_insert_query
        else:
            tablename = self.variable_table
            pk = self.variable_pk
            _insert_cmd = self._var_insert_query

        # Create temporary
        temp_name = "__" + tablename + str(random.randint(1000, 9999))
        with sa.create_engine(connstr).connect() as conn:
            kw = dict(temp=False, if_exists="replace", destroy=True)
            with TempTable(df, temp_name, conn, **kw):
                sql = _insert_cmd(df, tablename, temp_name, pk)
                conn.execute(sql)

        return None

    def get(self):
        "Convenience method to get a both DataFrames"
        v_df = self.variable_get()
        d_df = self.data_get()
        return [d_df, v_df]

    def put(self, connstr, dfs=None):
        "Convenience method to put both data and variables into table"
        if dfs is None:
            dfs = self.get()
        d_df, v_df = dfs

        self._put(connstr, "variable", v_df)
        self._put(connstr, "data", d_df)

        return None

