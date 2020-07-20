import pandas as pd
import requests
import us

from ...base import DatasetBaseNoDate
from ..base import ArcGIS


class Alabama(ArcGIS, DatasetBaseNoDate):
    ARCGIS_ID = "4RQmZZ0yaZkGR1zy"
    has_fips = True
    state_fips = int(us.states.lookup("Alabama").fips)
    source = "https://alpublichealth.maps.arcgis.com/apps/opsdashboard/index.html#/6d2771faa9da4a2786a509d82c8cf0f7"

    def __init__(self, params=None):
        if params is None:
            params = {
                "f": "json",
                "where": "1=1",
                "outFields": "*",
                "returnGeometry": "false",
            }

        super().__init__(params=params)

    def get(self):
        df = self.get_all_sheet_to_df(
            service="COVID19_ALCountiesData", sheet=1, srvid=1
        )
        # Rename columns
        renamed = df.rename(
            columns={
                "NAME": "county",
                "FIPS": "fips",
                "ConfirmedCases": "cases_confirmed",
                "Recovered": "recovered_total",
                "COVID_Deaths": "deaths_confirmed",
                "DateReported": "dt",
            }
        )

        renamed["negative_tests_total"] = renamed.LabTestCount - renamed.cases_confirmed

        renamed = renamed[
            [
                "dt",
                "county",
                "fips",
                "cases_confirmed",
                "recovered_total",
                "deaths_confirmed",
                "negative_tests_total",
            ]
        ]
        renamed["dt"] = renamed["dt"].map(
            lambda x: pd.datetime.fromtimestamp(x / 1000).date()
        )
        renamed = (
            renamed.set_index(["dt", "county"])
            .fillna(0)
            .astype(int)
            .reset_index()
            .sort_values(["dt", "county"])
            .melt(
                id_vars=["dt", "county", "fips"],
                var_name="variable_name",
                value_name="value",
            )
            .assign(vintage=pd.Timestamp.utcnow().normalize())
        )

        return renamed
