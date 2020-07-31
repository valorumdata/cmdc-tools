import pandas as pd
import requests
import us

from ...base import DatasetBaseNoDate
from ..base import ArcGIS


class AlabamaFips(ArcGIS, DatasetBaseNoDate):
    ARCGIS_ID = "4RQmZZ0yaZkGR1zy"
    has_fips = True
    state_fips = int(us.states.lookup("Alabama").fips)
    source = (
        "https://alpublichealth.maps.arcgis.com/apps/opsdashboard/"
        "index.html#/6d2771faa9da4a2786a509d82c8cf0f7"
    )

    def _get_statehosp(self):
        df = self.get_all_sheet_to_df("HospitalizedPatientTemporal_READ_ONLY", 1, 7)

        # WARNING: This is a 2020 specific operation... Will break in 2021
        df["dt"] = pd.to_datetime("2020-" + df["DateTxt"])
        df = df.rename(
            columns={"Confirmed_AllWeekdays": "hospital_beds_in_use_covid_total"}
        ).loc[:, ["dt", "hospital_beds_in_use_covid_total"]]
        df["fips"] = self.state_fips

        out = df.melt(id_vars=["dt", "fips"], var_name="variable_name")

        return out

    def _get_hosp(self):
        df = self.get_all_sheet_to_df("c19v2_hcw_ltcf_PUBLIC", 1, 7)
        renamed = df.rename(
            columns={
                "CLN_ICU": "cumulative_icu",
                "CLN_VENT": "cumulative_ventilators",
                "hospitalization": "cumulative_hospitalizations",
            }
        )
        renamed["fips"] = self.state_fips
        renamed["dt"] = pd.Timestamp.today().normalize()
        return renamed[
            [
                "dt",
                "fips",
                "cumulative_icu",
                "cumulative_ventilators",
                "cumulative_hospitalizations",
            ]
        ].melt(id_vars=["dt", "fips"], var_name="variable_name")

    def _get_cases_deaths_current_tests(self):

        df = (
            self.get_all_sheet_to_df("COV19_Public_Dashboard_ReadOnly", 0, 7)
            .rename(
                columns={
                    "CNTYFIPS": "fips",
                    "CONFIRMED": "cases_confirmed",
                    "DIED": "deaths_confirmed",
                    "LabTestCount": "tests_total",
                }
            )
            .loc[:, ["fips", "cases_confirmed", "deaths_confirmed", "tests_total"]]
        )

        df["fips"] = df["fips"].astype(int)
        df["dt"] = self._retrieve_dt("US/Central")

        df2 = (
            self.get_all_sheet_to_df("COVID19_probable_confirmed_PUBLIC", 1, 7)
            .rename(
                columns={
                    "FIPS": "fips",
                    "PROBABLE": "cases_suspected",
                    "PROBABLE_DEATH": "deaths_suspected",
                }
            )
            .loc[:, ["fips", "cases_suspected", "deaths_suspected"]]
        )

        # Join the two dfs
        dfs = df.merge(df2, on="fips", how="outer")

        dfs["cases_total"] = dfs.eval("cases_confirmed + cases_suspected")
        dfs["deaths_total"] = dfs.eval("deaths_confirmed + deaths_suspected")

        out = dfs.melt(id_vars=["dt", "fips"], var_name="variable_name").dropna()
        out["value"] = out["value"].astype(int)

        return out

    def get(self):
        pub = self._get_cases_deaths_current_tests()
        # TODO: This is commented out because (1) we don't currently have
        # any cumulative variables and (2) the data doesn't line up with
        # the dashboard numbers...
        # hosp = self._get_hosp()
        sthosp = self._get_statehosp()

        result = pd.concat([pub, sthosp], axis=0, ignore_index=True, sort=False).query(
            "fips != 99999"
        )
        result["vintage"] = self._retrieve_vintage()

        return result


class AlabamaCounty(AlabamaFips, DatasetBaseNoDate):
    ARCGIS_ID = "4RQmZZ0yaZkGR1zy"
    has_fips = False
    state_fips = int(us.states.lookup("Alabama").fips)
    source = "https://alpublichealth.maps.arcgis.com/apps/opsdashboard/index.html#/6d2771faa9da4a2786a509d82c8cf0f7"

    def get(self):
        tests = self._get_lab_test_summary()

        result = pd.concat([tests], axis=0, ignore_index=True)
        result["vintage"] = self._retrieve_vintage()

        return result

    def _get_lab_test_summary(self):
        df = self.get_all_sheet_to_df("Labtest_Summary_by_County_PUBLIC", 1, 7).rename(
            columns={"Jurisdiction": "county", "LabTestCount": "tests_total",}
        )

        df["dt"] = pd.to_datetime("2020-" + df["DateTxt"])

        # Pivot this because they don't report cumulative
        pt = df.pivot_table(
            index="dt", columns="county", values="tests_total"
        ).sort_index()
        pt = pt.cumsum().reset_index()

        # Reshape how we want
        out = pt.melt(id_vars="dt", var_name="county", value_name="value").dropna()
        out["value"] = out["value"].astype(int)
        out["county"] = out["county"].str.title()
        out["variable_name"] = "tests_total"

        return out
