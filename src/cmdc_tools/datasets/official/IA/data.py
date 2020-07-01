import pandas as pd
import us

from ...base import DatasetBaseNoDate
from ..base import ArcGIS


class Iowa(ArcGIS, DatasetBaseNoDate):
    ARCGIS_ID = "vPD5PVLI6sfkZ5E4"
    fips = int(us.states.lookup("Iowa").fips)
    has_fips = False
    source = "https://coronavirus.iowa.gov/pages/rmcc-data"

    def get(self):
        pass

    def _get_cases(self):
        df = self.get_all_sheet_to_df("IA_COVID19_Cases", 0, "")

        renamed = df.rename(
            columns={
                "FIPS": "fips",
                "Confirmed": "cases_confirmed",
                "Recovered": "recovered_total",
                "Deaths": "deaths_total",
                "last_updated": "dt",
            }
        )

        renamed["dt"] = renamed["dt"].map(lambda x: pd.datetime.fromtimestamp(x / 1000))

        return renamed[
            ["dt", "fips", "cases_confirmed", "recovered_total", "deaths_total"]
        ].sort_values(["dt", "fips"])

    def _get_hosp(self):
        df = self.get_all_sheet_to_df("COVID19_RMCC_Hospitalization", 0, "")
        reanmed = df.rename(
            columns={
                "RMCC": "region",
                "Total_Inpatient_Beds_Available": "hospital_beds_capacity_count",
                "Total_Hospitalized": "hospital_beds_in_use_any",
                "ICU": "icu_beds_in_use_any",
                "Ventilators_Available": "ventilators_capacity_count",
                "Ventilator": "ventilators_in_use_any",
            }
        )

        renamed["dt"] = pd.Timestamp.utcnow().normalize()
        return reanmed[
            [
                "dt",
                "region",
                "hospital_beds_capacity_count",
                "hospital_beds_in_use_any",
                "icu_beds_in_use_any",
                "ventilators_capacity_count",
                "ventilators_in_use_any",
            ]
        ]
