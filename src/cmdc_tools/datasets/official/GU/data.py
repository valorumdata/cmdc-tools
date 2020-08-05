import pandas as pd
import us

from ...base import DatasetBaseNoDate
from ..base import ArcGIS


class Guam(ArcGIS, DatasetBaseNoDate):
    ARCGIS_ID = "FPJlJZYRsD8OhCWA"
    source = "http://dphss.guam.gov/covid-19/"
    state_fips = int(us.states.lookup("Guam").fips)
    has_fips = True

    def get(self):
        nation = self._get_nationwide()

        # For now, not retrieving village data because they don't
        # have a fips code... We could easily reincorporate it
        # village = self._get_village()

        return nation

    def _get_nationwide(self):
        # Retrieve data and rename relevant columns
        df = self.get_all_sheet_to_df("Cases_Recovered_Deaths_Query", 0, 2)
        df = df.rename(
            columns={
                "Date": "dt",
                "Cases": "cases_total",
                "Recovered": "recovered_total",
                "Deaths": "deaths_total",
                "Active": "active_total",
            }
        )

        # Map to datetime and add fips
        df["dt"] = df["dt"].map(lambda x: self._esri_ts_to_dt(x))
        df["fips"] = self.state_fips

        # Reshape and return
        keepers = [
            "dt",
            "fips",
            "cases_total",
            "deaths_total",
            "active_total",
        ]
        out = df.loc[:, keepers].melt(
            id_vars=["dt", "fips"], var_name="variable_name", value_name="value"
        )
        out["vintage"] = self._retrieve_vintage()

        return out

    def _get_village(self):
        df = self.get_all_sheet_to_df("Village_Query", 0, 2)

        df = df.fillna(0)

        renamed = df.rename(
            columns={
                "Village": "village",
                "Cases": "cases_suspected",
                "Recoveries": "recovered_total",
            }
        )

        renamed["dt"] = self._retrieve_dt("Pacific/Guam")
        return renamed[["dt", "village", "cases_suspected", "recovered_total"]]
