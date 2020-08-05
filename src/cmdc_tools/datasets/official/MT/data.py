import pandas as pd
import requests
import textwrap

import us

from ..base import ArcGIS
from ...base import DatasetBaseNoDate


class Montana(DatasetBaseNoDate, ArcGIS):
    ARCGIS_ID = "qnjIrwR8z5Izc0ij"
    source = (
        "https://montana.maps.arcgis.com/apps/MapSeries"
        "/index.html?appid=7c34f3412536439491adcc2103421d4b"
    )
    state_fips = int(us.states.lookup("Montana").fips)
    has_fips = False

    def get(self):
        dt = self._retrieve_dt("US/Mountain")
        df = self.get_all_sheet_to_df("COVID_Cases_Production_View", 2, "")
        df = df.rename(columns={"County": "county"})

        # get cases
        case_outcome = self.get_cases(df)
        # get hospitalzation
        hbiuc = self.get_hospitalization_stats(df)

        return (
            case_outcome
            # Join tables together
            .join(hbiuc)
            # Reset index
            .reset_index()
            # Melt
            .melt(id_vars=["county"], var_name="variable_name")
            # Normalize
            .assign(vintage=dt, dt=dt)
        )

    def get_cases(self, df):

        case_outcome = (
            df.groupby(["county", "Outcome"])["Sex"]
            .count()
            .unstack(level="Outcome")
            .fillna(0)
            .astype(int)
            .rename(
                columns={
                    "Active": "active_total",
                    "Deceased": "deaths_total",
                    "Recovered": "recovered_total",
                }
            )
        )

        return case_outcome

    def get_hospitalization_stats(self, df):
        hbiuc = (
            df.groupby(["county", "Hospitalization"])["Sex"]
            .count()
            .unstack(level="Hospitalization")
            .fillna(0)
            .astype(int)["Y"]
            .rename("hospital_beds_in_use_covid_total")
        )
        return hbiuc
