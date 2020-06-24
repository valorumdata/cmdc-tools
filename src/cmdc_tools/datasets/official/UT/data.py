import pandas as pd

from ...base import DatasetBaseNoDate
from ..base import ArcGIS


class Utah(ArcGIS, DatasetBaseNoDate):
    ARCGIS_ID = "KaHXE9OkiB9e63uE"

    def get(self):
        df = self.get_all_sheet_to_df(
            "Utah_COVID19_Cases_by_Local_Health_Department_over_time", sheet=0, srvid=6
        )

        renamed = df.rename(
            columns={
                "COVID_Cases_Total": "cases_total",
                "Day": "dt",
                "Hospitalizations": "cumulative_hospitalized",
                "DISTNAME": "region",
            }
        )

        renamed["dt"] = renamed["dt"].map(lambda x: pd.datetime.fromtimestamp(x / 1000))

        # Keep only region rows
        # counties = renamed.loc[renamed.region.str.contains("County")]

        return (
            renamed[["dt", "region", "cases_total", "cumulative_hospitalized"]]
            .sort_values(["dt", "region"])
            .melt(id_vars=["dt", "region"], var_name="variable_name")
        )
