import textwrap

import pandas as pd

import us

from ..base import ArcGIS, CountyData
from ... import DatasetBaseNoDate


def fips_lookup(x):
    state = us.states.lookup(x)

    if state is None:
        return -1
    else:
        return int(state.fips)


class HHS(DatasetBaseNoDate, ArcGIS):
    """
    This scraper retrieves the hospital data provided by HHS at:

      https://protect-public.hhs.gov/pages/hospital-capacity

    It includes information on hospital capacity, hospital beds in use,
    hospital beds in use by covid patients, icu capacity, icu beds in
    use, and icu beds in use by covid patients
    """

    ARCGIS_ID = "qWZ7BaZXaP5isnfT"
    table_name = "hhs_covid"
    pk = '("vintage", "dt", "fips", "variable_id")'
    has_fips = True
    state_fips = 0  # Using 0 to denote that this is a national database
    source = "https://protect-public.hhs.gov/pages/hospital-capacity"
    provider = "HHS"

    def __init__(self, params=None):
        super(ArcGIS, self).__init__()

        # Default parameter values
        if params is None:
            params = {
                "f": "json",
                "where": "1=1",
                "outFields": "*",
                "returnGeometry": "false",
                "token": "",
            }

        self.params = params

    def _insert_query(self, df: pd.DataFrame, table_name: str, temp_name: str, pk: str):
        out = f"""
        INSERT INTO data.{table_name} (vintage, dt, fips, variable_id, value)
        SELECT tt.vintage, tt.dt, tt.fips, mv.id as variable_id, tt.value
        FROM {temp_name} tt
        LEFT JOIN meta.covid_variables mv ON tt.variable_name=mv.name
        ON CONFLICT {pk} DO UPDATE SET value = excluded.value
        """

        return textwrap.dedent(out)

    def _get_hospital_census(self):
        crename = {
            "state_name": "state",
            "total_icu_beds": "icu_beds_capacity_count",
            "icu_beds_used_estimate": "icu_beds_in_use_any",
            # "icu_beds_used_covid_est": "icu_beds_in_use_covid_total",
            "total_inpatient_beds": "hospital_beds_capacity_count",
            "inpatient_beds_used_estimate": "hospital_beds_in_use_any",
            "inpatient_beds_used_covid_est": "hospital_beds_in_use_covid_total",
        }
        df = (
            self.get_all_sheet_to_df(
                "State_Representative_Estimates_for_Hospital_Utilization", 0, 5
            )
            .rename(columns=crename)
            .loc[:, crename.values()]
        )

        out = df.melt(id_vars=["state"], var_name="variable_name")

        return out

    def _get_num_reporting(self):
        crename = {
            "state_name": "state",
            "reporting_hospitals": "num_hospitals_reporting",
            "total_hospitals": "num_of_hospitals",
        }
        df = (
            self.get_all_sheet_to_df("Hospitals_Reporting_State_Level", 0, 5)
            .rename(columns=crename)
            .loc[:, crename.values()]
        )

        out = df.melt(id_vars=["state"], var_name="variable_name")

        return out

    def get(self):
        df = pd.concat(
            [self._get_num_reporting(), self._get_hospital_census()],
            axis=0,
            ignore_index=True,
        )

        # Map state name to fips code and then drop state name
        df["fips"] = df["state"].map(lambda x: fips_lookup(x))
        df = df.drop(["state"], axis=1).query("fips > 0")

        df["dt"] = (
            pd.Timestamp.utcnow().tz_convert("US/Eastern").tz_localize(None).normalize()
        )
        df["vintage"] = pd.Timestamp.utcnow().normalize()

        # We are storing everything as integers so we need to convert
        # the numbers from estimated floats to integers...
        df = df.dropna()
        df["value"] = df["value"].astype(int)

        return df
