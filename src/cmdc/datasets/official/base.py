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

    def arcgis_query_url(self, service, sheet, srvid=1):
        out = f"https://services{srvid}.arcgis.com/{self.ARCGIS_ID}/"
        out += f"ArcGIS/rest/services/{service}/FeatureServer/{sheet}/query"

        return out

