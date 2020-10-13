import textwrap

import pandas as pd
import us

from ...base import DatasetBaseNoDate
from ..base import ArcGIS


class Pennsylvania(DatasetBaseNoDate, ArcGIS):
    ARCGIS_ID = "Nifc7wlHaBPig3Q3"
    source = (
        "https://experience.arcgis.com/experience/" "ed2def13f9b045eda9f7d22dbc9b500e/"
    )
    state_fips = int(us.states.lookup("Pennsylvania").fips)
    has_fips = False

    def _get_cd(self):
        df = self.get_all_sheet_to_df(service="COVID_PA_Counties", sheet=0, srvid=1)

        column_map = {
            "County": "county",
            "Cases": "cases_total",
            "Probable": "cases_suspected",
            "Deaths": "deaths_total",
            "Confirmed": "positive_tests_total",
            "Negative": "negative_tests_total",
            # "TotalTests": "tests_total",  # Doesn't exist but we want column later
        }
        df = df.rename(columns=column_map).loc[:, column_map.values()]

        # Adjust current columns and add new ones
        df["tests_total"] = df.eval("positive_tests_total + negative_tests_total")

        out = df.melt(id_vars=["county"], var_name="variable_name").dropna()
        out["value"] = out["value"].astype(int)
        out["dt"] = self._retrieve_dt("US/Eastern")

        return out

    def _get_hosp(self):
        df = self.get_all_sheet_to_df(service="covid_hosp", sheet=0, srvid=1)

        column_map = {
            "County": "county",
            "date": "dt",
            "med_total": "hospital_beds_capacity_count",
            "covid_patients": "hospital_beds_in_use_covid_total",
            "icu_total": "icu_beds_capacity_count",
            "vents": "ventilators_capacity_count",
            "vents_use": "ventilators_in_use_any",
            "covid_vents": "ventilators_in_use_covid_total",
        }
        df = df.rename(columns=column_map).loc[:, column_map.values()]
        df["dt"] = df["dt"].map(self._esri_ts_to_dt)

        # Adjust current columns and add new ones
        df["hospital_beds_capacity_count"] += df["icu_beds_capacity_count"]

        # Reshape
        out = df.melt(id_vars=["county", "dt"], var_name="variable_name").dropna()
        out["value"] = out["value"].astype(int)

        return out

    def get(self):
        # Read in the right services
        df_cd = self._get_cd()
        df_hosp = self._get_hosp()

        out = pd.concat([df_cd, df_hosp], axis=0, ignore_index=True, sort=False)
        out["vintage"] = self._retrieve_vintage()

        return out
