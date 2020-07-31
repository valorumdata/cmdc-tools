import pandas as pd
import requests
import us

from ..base import CountyData
from ...base import DatasetBaseNoDate


class Indiana(DatasetBaseNoDate, CountyData):
    source = "https://www.coronavirus.in.gov/2393.htm"
    has_fips = True
    state_fips = int(us.states.lookup("Indiana").fips)

    def get(self):
        hosp = self._get_hosp()
        cd = self._get_case_deaths()

        out = pd.concat([hosp, cd], sort=False).sort_values(["dt", "fips"])
        out["vintage"] = self._retrieve_vintage()

        return out

    def _make_json_req(self):
        url = (
            "https://www.coronavirus.in.gov/map/"
            "covid-19-indiana-daily-report-current.topojson"
        )

        res = requests.get(url)

        return res

    def _get_case_deaths(self):
        # Get the result object
        res = self._make_json_req()

        # Get the state and county data
        state = self._extract_state_case_deaths(res)
        county = self._extract_county_case_deaths(res)

        # Melt stuff to the right shape
        result = pd.concat([state, county], axis=0, ignore_index=True)

        return result

    def _extract_state_case_deaths(self, res):
        # Pull out the `viz_date` data that has the time-series of
        # cases/deaths/tests
        state = pd.DataFrame(res.json()["objects"]["viz_date"])
        state = state.rename(
            columns={
                "DATE": "dt",
                "COVID_COUNT_CUMSUM": "cases_total",
                "COVID_DEATHS_CUMSUM": "deaths_total",
                "COVID_TEST_CUMSUM": "total_test",
            }
        )

        # Convert to datetime and set the FIPS code to the state values
        state["dt"] = pd.to_datetime(state["dt"])
        state["fips"] = self.state_fips

        state = state.loc[:, ["dt", "fips", "cases_total", "deaths_total"]]
        state = state.melt(
            id_vars=["dt", "fips"], var_name="variable_name", value_name="value"
        )

        return state

    def _extract_county_case_deaths(self, res):
        county_jsons = res.json()["objects"]["cb_2015_indiana_county_20m"]["geometries"]

        # Will create a DataFrame for each county and then stack them
        dfs = []
        crename = {
            "DATE": "dt",
            "COVID_COUNT_CUMSUM": "cases_total",
            "COVID_DEATHS_CUMSUM": "deaths_total",
            "COVID_TEST_CUMSUM": "test_total",
        }

        for _county in county_jsons:
            _df = pd.DataFrame.from_records(_county["properties"]["VIZ_DATE"]).rename(
                columns=crename
            )

            _df["dt"] = pd.to_datetime(_df["dt"])
            _df["fips"] = int(_county["properties"]["GEOID"])

            dfs.append(_df.loc[:, ["dt", "fips", "cases_total", "deaths_total"]])

        county = pd.concat(dfs, axis=0, ignore_index=True).melt(
            id_vars=["dt", "fips"], var_name="variable_name", value_name="value"
        )

        return county

    def _get_hosp(self):
        url = (
            "https://www.coronavirus.in.gov/map/"
            "covid-19-indiana-universal-report-current-public.json"
        )

        res = requests.get(url)
        df = pd.DataFrame(res.json()["metrics"]["data"])

        df = df.rename(
            columns={
                "date": "dt",
                "district": "fips",
                "m1a_beds_all_occupied_beds_covid_19_smoothed": "hospital_beds_in_use_covid_total",
                "m2b_hospitalized_icu_supply": "icu_beds_capacity_count",
                "m2b_hospitalized_icu_occupied_covid": "icu_beds_in_use_covid_total",
                "m2b_hospitalized_icu_occupied_non_covid": "icu_beds_in_use_noncovid",
                "m2b_hospitalized_vent_supply": "ventilators_capacity_count",
                "m2b_hospitalized_vent_occupied_covid": "ventilators_in_use_covid_total",
                "m2b_hospitalized_vent_occupied_non_covid": "ventilators_in_use_noncovid",
            }
        )

        # To datetime and create new variables
        df["dt"] = pd.to_datetime(df["dt"])
        df["icu_beds_in_use_any"] = df.eval(
            "icu_beds_in_use_covid_total + icu_beds_in_use_noncovid"
        )
        df["ventilators_in_use_any"] = df.eval(
            "ventilators_in_use_covid_total + ventilators_in_use_noncovid"
        )

        # Only keep data that we want
        cols_to_keep = [
            "dt",
            "fips",
            "district_type",
            "hospital_beds_in_use_covid_total",
            "icu_beds_capacity_count",
            "icu_beds_in_use_covid_total",
            "icu_beds_in_use_any",
            "ventilators_capacity_count",
            "ventilators_in_use_covid_total",
            "ventilators_in_use_any",
        ]
        df = (
            df.loc[:, cols_to_keep]
            .astype(
                {
                    "fips": int,
                    "icu_beds_capacity_count": int,
                    "icu_beds_in_use_covid_total": int,
                    "icu_beds_in_use_any": int,
                    "ventilators_capacity_count": int,
                    "ventilators_in_use_covid_total": int,
                    "ventilators_in_use_any": int,
                }
            )
            .query("district_type != 'd'")
        )

        # Set state-wide data fips code to Indiana's fips
        df["fips"] = df["fips"].where(df["district_type"] == "c", self.state_fips)
        df = df.drop("district_type", axis=1)

        out = df.melt(
            id_vars=["dt", "fips"], var_name="variable_name", value_name="value"
        )

        return out
