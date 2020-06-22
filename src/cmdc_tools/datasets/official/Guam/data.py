import pandas as pd

from ...base import DatasetBaseNoDate
from ..base import ArcGIS


class Guam(ArcGIS, DatasetBaseNoDate):
    ARCGIS_ID = "FPJlJZYRsD8OhCWA"

    def get(self):
        nation = self._get_nationwide()
        village = self._get_village()

        result = pd.concat([nation, village], sort=False)

        return result.melt(id_vars=["dt", "village"], var_name="variable_name",)

    def _get_nationwide(self):
        df = self.get_all_sheet_to_df("Cases_Recovered_Deaths_Query", 0, 2)

        renamed = df.rename(
            columns={
                "Date": "dt",
                "Cases": "cases_confirmed",
                "Recovered": "recovered_total",
                "Deaths": "deaths_confirmed",
                "Active": "active_total",
            }
        )

        renamed["dt"] = renamed["dt"].map(lambda x: pd.datetime.fromtimestamp(x / 1000))

        return renamed[
            [
                "dt",
                "cases_confirmed",
                "recovered_total",
                "deaths_confirmed",
                "active_total",
            ]
        ]

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

        renamed["dt"] = pd.Timestamp.utcnow().normalize()
        return renamed[["dt", "village", "cases_suspected", "recovered_total"]]
