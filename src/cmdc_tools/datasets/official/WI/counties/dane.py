import pandas as pd
import us

from ....base import DatasetBaseNoDate
from ...base import ArcGIS


class WIDane(DatasetBaseNoDate, ArcGIS):
    ARCGIS_ID = "lx96Ahunbwmk5g5p"
    source = (
        "https://cityofmadison.maps.arcgis.com/apps/opsdashboard/"
        "index.html#/e22f5ba4f1f94e0bb0b9529dc82db6a3"
    )
    county_fips = 25  # Dane County	025
    state_fips = int(us.states.lookup("Wisconsin").fips)
    has_fips = True

    def _get_case_death(self):
        crename = {
            "Date": "dt",
            "Total_cases": "cases_total",
            "Deaths": "deaths_total",
        }
        df = self.get_all_sheet_to_df("CaseCount_vw", 0, "")
        df = df.rename(columns=crename).loc[:, crename.values()]
        df = df.dropna(subset=["dt"])
        df["dt"] = pd.to_datetime(df["dt"] + "/2020")
        df = df.sort_values("dt")
        df["deaths_total"] = df["deaths_total"].fillna(0.0).cumsum()

        # Make sure things are integers
        df["cases_total"] = df["cases_total"].astype(int)
        df["deaths_total"] = df["deaths_total"].astype(int)

        # Reshape
        out = df.melt(id_vars=["dt"], var_name="variable_name")

        return out

    def _get_hospital(self):
        crename = {
            "Date": "dt",
            "Total_COVID_19_Patients_in_ICU": "icu_beds_in_use_covid_total",
            "Total_COVID_19_Inpatients": "hospital_beds_in_use_covid_total",
        }
        df = self.get_all_sheet_to_df("hospitalization_timeseries_ver3_0_vw", 0, "")
        df = df.rename(columns=crename).loc[:, crename.values()]
        df = df.dropna(subset=["dt"])
        df["dt"] = pd.to_datetime(df["dt"] + "/2020")
        df = df.sort_values("dt")

        # Make sure things are integers
        df["icu_beds_in_use_covid_total"] = df.eval(
            "icu_beds_in_use_covid_total"
        ).astype(int)
        df["hospital_beds_in_use_covid_total"] = df.eval(
            "hospital_beds_in_use_covid_total"
        ).astype(int)

        # Reshape
        out = df.melt(id_vars=["dt"], var_name="variable_name")

        return out

    def _get_tests(self):
        crename = {
            "Date": "dt",
            "Number_of_Tests_Administered": "tests_total",
        }
        df = self.get_all_sheet_to_df("tests_by_day_ver3_0_vw", 0, "")
        df = df.rename(columns=crename).loc[:, crename.values()]
        df = df.dropna(subset=["dt"])
        df["dt"] = pd.to_datetime(df["dt"] + "/2020")
        df = df.sort_values("dt")

        df["tests_total"] = df["tests_total"].cumsum().astype(int)

        # Reshape
        out = df.melt(id_vars=["dt"], var_name="variable_name")

        return out

    def get(self):
        out = pd.concat(
            [self._get_case_death(), self._get_hospital(), self._get_tests(),],
            axis=0,
            ignore_index=True,
        ).assign(
            vintage=pd.Timestamp.utcnow().normalize(),
            fips=self.state_fips * 1000 + self.county_fips,
        )

        return out
