import pandas as pd
import us

from ...base import DatasetBaseNoDate
from ..base import ArcGIS


class Iowa(ArcGIS, DatasetBaseNoDate):
    ARCGIS_ID = "vPD5PVLI6sfkZ5E4"
    state_fips = int(us.states.lookup("Iowa").fips)
    has_fips = True
    source = "https://coronavirus.iowa.gov/pages/rmcc-data"

    def get(self):
        cdt = self._get_cases()

        out = pd.concat([cdt], axis=0, ignore_index=True)
        out["vintage"] = pd.Timestamp.utcnow().normalize()

        return out

    def _get_cases(self):
        # Renamers
        crename = {
            "FIPS": "fips",
            "Confirmed": "cases_confirmed",
            "Recovered": "recovered_total",
            "Deaths": "deaths_total",
            "individuals_tested": "tests_total",
            "last_updated": "dt",
        }

        # Get DataFrame and rename cols
        df = self.get_all_sheet_to_df("IA_COVID19_Cases", 0, "")
        df = df.rename(columns=crename).loc[:, crename.values()]

        # Set date and make sure fips and other number columns
        # are integers
        df = df.apply(lambda x: pd.to_numeric(x, errors="ignore"))
        df["dt"] = df["dt"].map(self._esri_ts_to_dt).map(lambda x: x.date())

        # Reshape
        out = df.melt(id_vars=["dt", "fips"], var_name="variable_name")

        return out.query("fips != 0")

    def _get_hosp(self):
        # TODO: Once we decide how to treat hospital regions, return to
        # this getter and add it
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
