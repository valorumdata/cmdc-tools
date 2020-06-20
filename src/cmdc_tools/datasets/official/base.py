import pandas as pd
import requests
import textwrap

from .. import InsertWithTempTable


class CountyData(InsertWithTempTable):
    table_name = "us_covid"
    pk = '("vintage", "dt", "fips", "variable_id")'
    data_type = "covid"

    def __init__(self):
        super(CountyData, self).__init__()

        return None

    def _insert_query(
            self, df: pd.DataFrame, table_name: str, temp_name: str, pk: str,
            on_name=False
        ):
        if not on_name:
            out = f"""
            INSERT INTO data.{table_name} (
              vintage, dt, fips, variable_id, value
            )
            SELECT tt.vintage, tt.dt, tt.fips, mv.id as variable_id, tt.value
            FROM {temp_name} tt
            LEFT JOIN meta.covid_variables mv ON tt.variable_name=mv.name
            ON CONFLICT {pk} DO NOTHING
            """
        else:
            out = f"""
            INSERT INTO data.{table_name} (
              vintage, dt, fips, variable_id, value
            )
            SELECT tt.vintage, tt.dt, us.fips, mv.id as variable_id, tt.value
            FROM {temp_name} tt
            INNER JOIN meta.us_fips us on tt.county=us.name
            LEFT JOIN meta.covid_variables mv ON tt.variable_name=mv.name
            WHERE us.state = LPAD({self.state_fips}::TEXT, 2, '0')
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
                "f": "json",
                "where": "1=1",
                "outFields": "*",
                "returnGeometry": "false",
            }

        self.params = params

        return None

    def arcgis_query_url(self, service, sheet, srvid=1):
        out = f"https://services{srvid}.arcgis.com/{self.ARCGIS_ID}/"
        out += f"ArcGIS/rest/services/{service}/FeatureServer/{sheet}/query"

        return out

    def get_res_json(self, service, sheet, srvid, params):
        # Perform actual request
        url = self.arcgis_query_url(service=service, sheet=sheet, srvid=srvid)
        res = requests.get(url, params=params)

        return res.json()

    def arcgis_json_to_df(self, res_json):
        df = pd.DataFrame.from_records([x["attributes"] for x in res_json["features"]])

        return df

    def get_single_sheet_to_df(self, service, sheet, srvid, params):

        # Perform actual request
        res_json = self.get_res_json(service, sheet, srvid, params)

        # Turn into a DF
        df = self.arcgis_json_to_df(res_json)

        return df

    def get_all_sheet_to_df(self, service, sheet, srvid):
        # Get a copy so that we don't screw up main parameters
        curr_params = self.params.copy()

        # Get first request and detrmine number of requests that come per
        # response
        res_json = self.get_res_json(service, sheet, srvid, curr_params)
        total_offset = len(res_json["features"])

        # Use first response to create first DataFrame
        _dfs = [self.arcgis_json_to_df(res_json)]
        unbroken_chain = res_json.get("exceededTransferLimit", False)
        while unbroken_chain:
            # Update parameters and make request
            curr_params.update({"resultOffset": total_offset})
            res_json = self.get_res_json(service, sheet, srvid, curr_params)

            # Convert to DataFrame and store in df list
            _df = self.arcgis_json_to_df(res_json)
            _dfs.append(_df)

            total_offset += len(res_json["features"])
            unbroken_chain = res_json.get("exceededTransferLimit", False)

        # Stack these up
        df = pd.concat(_dfs)

        return df
