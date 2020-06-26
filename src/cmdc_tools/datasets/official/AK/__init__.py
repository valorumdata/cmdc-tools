import textwrap

import pandas as pd
import re

import us

from ..base import ArcGIS, CountyData
from ... import DatasetBaseNoDate

__all__ = ["Alaska"]


class Alaska(DatasetBaseNoDate, ArcGIS):
    """
    Other sheets of interest:

    * Geographic_Distribution_of_Hospital_Survey_Results: Hospital
      results as the region level
    * daily_testing_summary: Test count by county

    """

    ARCGIS_ID = "WzFsmainVTuD5KML"
    table_name = "us_covid"
    pk = '("vintage", "dt", "fips", "variable_id")'
    has_fips = True
    state_fips = int(us.states.lookup("Alaska").fips)
    source = (
        "https://www.arcgis.com/apps/opsdashboard/"
        "index.html#/83c63cfec8b24397bdf359f49b11f218"
    )

    def _insert_query(self, df: pd.DataFrame, table_name: str, temp_name: str, pk: str):
        out = f"""
        INSERT INTO data.{table_name} (
          vintage, dt, fips, variable_id, value
        )
        SELECT tt.vintage, tt.dt, tt.fips, mv.id as variable_id, tt.value
        FROM {temp_name} tt
        INNER JOIN meta.covid_variables mv ON tt.variable_name=mv.name
        INNER JOIN meta.us_fips using (fips)
        ON CONFLICT {pk} DO UPDATE set value = excluded.value
        """
        return textwrap.dedent(out)

    def get(self):
        # Retrieve each of the datasets
        s_cd = self.get_state_cases_deaths()
        s_hosp = self.get_state_hospitalization()
        s_test = self.get_state_testing()
        c_cdr = self.get_county_cases_deaths_recoveries()
        c_test = self.get_county_tests()

        result = pd.concat(
            [s_cd, s_hosp, s_test, c_cdr, c_test], axis=0, ignore_index=True, sort=False
        )
        result["vintage"] = pd.Timestamp.utcnow().normalize()

        return result

    def get_census_borough_areas_dict(self):
        # Retrieve census areas and boroughs
        df = self.get_all_sheet_to_df("Boroughs_Census_Areas", 0, 1)
        df["fips"] = (df["STATEFP10"] + df["COUNTYFP10"]).astype(int)
        df["name"] = df["NAMELSAD10"].str.lower()

        return dict(list(df[["name", "fips"]].to_records(index=False)))

    def get_state_cases_deaths(self):
        df = self.get_all_sheet_to_df("Daily_Cases_Hospitalizations_and_Deaths", 0, 1)

        # Rename and select subset
        crename = {
            "Date_Reported": "dt",
            "All_Cases__Cumulative_": "cases_total",
            "Deceased_Cases__Cumulative_": "deaths_total",
        }
        df = df.rename(columns=crename).loc[:, crename.values()]

        # Create date
        df["dt"] = df["dt"].map(
            lambda x: pd.Timestamp.fromtimestamp(x / 1000).normalize()
        )
        df["fips"] = self.state_fips

        out = df.melt(id_vars=["dt", "fips"], var_name="variable_name")

        return out

    def get_state_hospitalization(self):
        # Retrieve the hospitalization sheet
        df = self.get_all_sheet_to_df("COVID_Hospital_Dataset_(prod)", 0, 1)

        # Rename and select subset
        crename = {
            "Inpatient_Beds": "hospital_beds_capacity_count",
            "Inpatient_Occup": "hospital_beds_in_use_any",
            "ICU_Beds": "icu_beds_capacity_count",
            "ICU_Occup": "icu_beds_in_use_any",
            "Vent_Cap": "ventilators_capacity_count",
            "Vent_Occup": "ventilators_in_use_any",
        }
        df = df.rename(columns=crename).loc[:, crename.values()]
        df = df.melt(var_name="variable_name", value_name="value")
        df = df.groupby("variable_name")["value"].sum().reset_index()

        # Create date and vintage
        df["dt"] = (
            pd.Timestamp.utcnow().tz_convert("US/Alaska").normalize().tz_localize(None)
        )
        df["fips"] = self.state_fips

        return df.loc[:, ["dt", "fips", "variable_name", "value"]]

    def get_state_testing(self):
        df = self.get_all_sheet_to_df("Daily_Test_Positivity", 0, 1)

        # Rename and select subset
        crename = {
            "Date_": "dt",
            "daily_positive": "positive_tests_total",
            "daily_negative": "negative_tests_total",
            # "daily_tests": "tests_total",
        }
        df = df.rename(columns=crename).loc[:, crename.values()]
        df["dt"] = df["dt"].map(
            lambda x: pd.Timestamp.fromtimestamp(x / 1000).normalize()
        )
        df["fips"] = self.state_fips
        df = df.sort_values("dt")

        df["positive_tests_total"] = df["positive_tests_total"].cumsum()
        df["negative_tests_total"] = df["negative_tests_total"].cumsum()

        out = df.melt(
            id_vars=["dt", "fips"], var_name="variable_name", value_name="value"
        )

        return out

    def get_county_tests(self):
        # Get testing data
        df = self.get_all_sheet_to_df("COVID_Tests_Dataset", 0, 1)

        # Rename and select subset
        crename = {
            "CollectedDate": "dt",
            "CountyFIPS": "fips",
            "Results": "result",
        }
        df = df.rename(columns=crename).loc[:, crename.values()]
        df["fips"] = df["fips"].astype(int) + 1000 * self.state_fips
        df["dt"] = df["dt"].map(
            lambda x: pd.Timestamp.fromtimestamp(x / 1000).normalize()
        )

        # Count all of the positive/negative tests for each day/fips
        df = (
            df.groupby(["dt", "fips"])["result"]
            .apply(lambda x: x.value_counts())
            .unstack(level=-1)
            .fillna(0.0)
            .cumsum()
            .reset_index()
        )
        df = df.rename(
            columns={
                "Negative": "negatives_tests_total",
                "Positive": "positive_tests_total",
            }
        )

        out = df.melt(
            id_vars=["dt", "fips"], var_name="variable_name", value_name="value"
        )

        return out

    def get_county_cases_deaths_recoveries(self):
        # Retrieve the counties and case/death/recovered/active data
        cdict = self.get_census_borough_areas_dict()
        df = self.get_all_sheet_to_df("HospDecRecTable", 0, 1)

        # Rename and select subset
        crename = {
            "County": "county",
            "Total_Cases": "cases_total",
            "Deaths_Cumulative": "deaths_total",
            "Recoveries_Cumulative": "recovered_total",
            "Active_Cases": "active_total",
        }
        df = df.rename(columns=crename).loc[:, crename.values()]
        df["fips"] = df["county"].map(lambda x: cdict[x.lower()])
        df["dt"] = (
            pd.Timestamp.utcnow().tz_convert("US/Alaska").normalize().tz_localize(None)
        )
        df = df.drop(["county"], axis=1)

        out = df.melt(
            id_vars=["dt", "fips"], var_name="variable_name", value_name="value"
        )

        return out
