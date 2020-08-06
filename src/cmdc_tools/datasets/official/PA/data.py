import textwrap

import pandas as pd
import us

from ...base import DatasetBaseNoDate
from ..base import ArcGIS


class Pennsylvania(DatasetBaseNoDate, ArcGIS):
    ARCGIS_ID = "xtuWQvb2YQnp0z3F"
    source = (
        "https://experience.arcgis.com/experience/" "cfb3803eb93d42f7ab1c2cfccca78bf7/"
    )
    state_fips = int(us.states.lookup("Pennsylvania").fips)
    has_fips = False

    def get(self):
        df = self.get_all_sheet_to_df(
            service="Pennsylvania_Public_COVID19_Dashboard_Data", sheet=0, srvid=2
        )

        column_map = {
            "County": "county",
            "Cases": "cases_total",
            "Probable": "cases_suspected",
            "Deaths": "deaths_total",
            "Confirmed": "positive_tests_total",
            "Negative": "negative_tests_total",
#             "Adult_ICU_Beds_Available": "icu_beds_available",
            "Adult_ICU_staffed": "icu_beds_capacity_count",
#             "Med_Surg_Beds_Available": "hospital_beds_available",
            "Med_Surg_Staffed": "hospital_beds_capacity_count",
            "COVID19_Hospitalizations": "hospital_beds_in_use_covid_total",
            "Total_Ventilators": "ventilators_capacity_count",
            "Ventilators_in_use": "ventilators_in_use_any",
            "COVID19_Ventilators": "ventilators_in_use_covid_total",
#             "TotalTests": "tests_total",  # Doesn't exist but we want column later
        }
        df = df.rename(columns=column_map)
        df["hospital_beds_capacity_count"] += df["icu_beds_capacity_count"]

        df["tests_total"] = df.eval("positive_tests_total + negative_tests_total")
        df = df.loc[:, list(column_map.values())]

        out = df.melt(id_vars=["county"], var_name="variable_name").dropna()
        out["value"] = out["value"].astype(int)
        out["dt"] = self._retrieve_dt("US/Eastern")
        out["vintage"] = self._retrieve_vintage()

        return out
