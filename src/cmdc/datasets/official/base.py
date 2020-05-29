import pandas as pd
import textwrap

from cmdc.datasets import OnConflictNothingBase


class CountyData(OnConflictNothingBase):
    table_name = "us_covid"
    pk = '("vintage", "dt", "fips", "variable_id")'

    def __init__(self):
        super(CountyData, self).__init__()

        return None

    def _insert_query(self, df, table_name, temp_name, pk):
        out = f"""
        INSERT INTO data.{table_name} (vintage, dt, fips, variable_id, value)
        SELECT tt.vintage, tt.dt, tt.fips, mv.id as variable_id, tt.value
        FROM {temp_name} tt
        LEFT JOIN meta.covid_variables mv ON tt.variable_name=mv.name
        ON CONFLICT {pk} DO NOTHING
        """

        return textwrap.dedent(out)

    def get(self):

        df = pd.read_csv(CA_COUNTY_URL)
        df = df.rename(columns=C_RENAMER).loc[:, list(C_RENAMER.values())]
        df["dt"] = pd.to_datetime(df["dt"])
        df["vintage"] = pd.datetime.today()

        # Create totals
        df["hospital_beds_in_use_covid_total"] = df.eval(
            "hospital_beds_in_use_covid_confirmed + hospital_beds_in_use_covid_suspected"
        )
        df["icu_beds_in_use_covid_total"] = df.eval(
            "icu_beds_in_use_covid_confirmed + icu_beds_in_use_covid_suspected"
        )

        df = df.melt(
            id_vars=["vintage", "dt", "name"],
            var_name="variable_name", value_name="value"
        )

        return df


class ArcGIS(CountyData):
    """
    Must define class variables:

    * `ARCGIS_ID`
    * `FIPS`

    in order to use this class
    """

    def __init__(self, params=None):
        super(ArcGIS, self).__init__()

        # Default parameter values
        if params is None:
            params = {
                "where": "0=0",
                "outFields": "*",
                "returnGeometry": "false",
                "f": "pjson"
            }
        self.params = params

        return None

    def arcgis_query_url(self, service, sheet):
        out = f"http://services1.arcgis.com/{self.ARCGIS_ID}/"
        out += f"ArcGIS/rest/services/{service}/FeatureServer/{sheet}/query"

        return out

