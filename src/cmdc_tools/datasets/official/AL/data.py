import pandas as pd
import requests
import us

from ...base import DatasetBaseNoDate
from ..base import ArcGIS


class AlabamaFips(ArcGIS, DatasetBaseNoDate):
    ARCGIS_ID = "4RQmZZ0yaZkGR1zy"
    has_fips = True
    state_fips = int(us.states.lookup("Alabama").fips)
    source = "https://alpublichealth.maps.arcgis.com/apps/opsdashboard/index.html#/6d2771faa9da4a2786a509d82c8cf0f7"

    def get(self):
        public = self._get_public_dashboard()
        hosp = self._get_hosp()
        concat = pd.concat([public, hosp], sort=False)
        result = concat[concat.fips != 99999]
        return result

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
        return (
            renamed[
                [
                    "dt",
                    "fips",
                    "cumulative_icu",
                    "cumulative_ventilators",
                    "cumulative_hospitalizations",
                ]
            ]
            .melt(id_vars=["dt", "fips"], var_name="variable_name")
            .assign(vintage=pd.Timestamp.utcnow())
        )

    def _get_public_dashboard(self):
        df = self.get_all_sheet_to_df("COV19_Public_Dashboard_ReadOnly", 0, 7)
        renamed = df.rename(
            columns={
                "CNTYFIPS": "fips",
                "CONFIRMED": "cases_confirmed",
                "DIED": "deaths_total",
                "LabTestCount": "tests_total",
            }
        )
        renamed.fips = renamed.fips.astype(int)
        return (
            renamed[["fips", "cases_confirmed", "deaths_total", "tests_total"]]
            .melt(id_vars=["fips"], var_name="variable_name")
            .assign(vintage=pd.Timestamp.utcnow(), dt=pd.Timestamp.today().normalize())
        )


class AlabamaCounty(AlabamaFips, DatasetBaseNoDate):
    ARCGIS_ID = "4RQmZZ0yaZkGR1zy"
    has_fips = False
    state_fips = int(us.states.lookup("Alabama").fips)
    source = "https://alpublichealth.maps.arcgis.com/apps/opsdashboard/index.html#/6d2771faa9da4a2786a509d82c8cf0f7"

    def get(self):
        tests = self._get_lab_test_summary()
        return tests
        # return pd.concat([tests], sort=False)

    def _get_lab_test_summary(self):
        df = self.get_all_sheet_to_df("Labtest_Summary_by_County_PUBLIC", 1, 7)
        renamed = df.rename(
            columns={
                "DateTxt": "dt",
                "Jurisdiction": "county",
                "LabTestCount": "tests_total",
            }
        )
        renamed.dt = renamed.dt + "-2020"
        renamed.dt = pd.to_datetime(renamed.dt)
        renamed = (
            renamed.set_index("dt")
            .tz_localize("US/Central")
            .tz_convert("UTC")
            .reset_index()
        )
        return (
            renamed[["dt", "county", "tests_total"]]
            .sort_values(["dt", "county"])
            .melt(id_vars=["dt", "county"], var_name="variable_name")
            .assign(vintage=pd.Timestamp.utcnow())
        )

    # def _get_confirmed(self):
    #     df = self.get_all_sheet_to_df("Daily_Confirmed_by_County_PUBLIC", 1, 7)
    #     renamed = df.rename(
    #         columns={
    #             "Jurisdiction": "county",
    #             "DateTxt": "dt",
    #             "Confirmed": "cases_confirmed",
    #         }
    #     )
    #     renamed.dt = renamed.dt + "-2020"
    #     renamed.dt = pd.to_datetime(renamed.dt)
    #     return renamed[["county", "dt", "cases_confirmed"]]
