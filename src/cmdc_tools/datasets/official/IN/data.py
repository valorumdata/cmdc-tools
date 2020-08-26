import pandas as pd
import requests
import us

from ...base import DatasetBaseNoDate
from ..base import CountyData


class Indiana(DatasetBaseNoDate, CountyData):
    source = "https://www.coronavirus.in.gov/2393.htm"
    has_fips = True
    state_fips = int(us.states.lookup("Indiana").fips)

    def get(self):
        res = self._make_json_req()
        metricsdata = self._extract_data(res)

        out = pd.concat([metricsdata], sort=False).sort_values(["dt", "fips"])
        out["vintage"] = self._retrieve_vintage()

        return out

    def _make_json_req(self):
        url = (
            "https://www.coronavirus.in.gov/map/"
            "covid-19-indiana-universal-report-current-public.json"
        )

        res = requests.get(url)

        if res.status_code is not 200:
            raise ValueError("JSON request failed")

        return res

    def _extract_data(self, res):
        # Put into dataframe and dump garbage district... No idea why
        # it shows up but it isn't an Indiana fips code (18901, the
        # garbage district, does not show up as of August 26 but will
        # leave the filter just in case it reappears
        df = pd.DataFrame(res.json()["metrics"]["data"])
        df = df.query("district != '18901'")

        # Variables of interest
        column_names = {
            # Descriptive
            "date": "dt",
            "district": "fips",
            # Case/Death/Test variables
            "m1e_covid_cases_cumsum": "cases_confirmed",
            "m1e_covid_cases_prob_cumsum": "cases_suspected",
            "m1e_covid_deaths_cumsum": "deaths_confirmed",
            "m1e_covid_deaths_prob_cumsum": "deaths_suspected",
            "m1e_covid_tests_cumsum": "tests_total",
            # Hospitalization/ICU/Ventilator variables
            "m1a_beds_all_occupied_beds_covid_19_smoothed": "hospital_beds_in_use_covid_total",
            "m2b_hospitalized_icu_supply": "icu_beds_capacity_count",
            "m2b_hospitalized_icu_occupied_covid": "icu_beds_in_use_covid_total",
            "m2b_hospitalized_icu_occupied_non_covid": "icu_beds_in_use_noncovid",
            "m2b_hospitalized_vent_supply": "ventilators_capacity_count",
            "m2b_hospitalized_vent_occupied_covid": "ventilators_in_use_covid_total",
            "m2b_hospitalized_vent_occupied_non_covid": "ventilators_in_use_noncovid",
        }
        df = df.rename(columns=column_names)

        # Convert date to datetime
        df["dt"] = pd.to_datetime(df["dt"])

        # Create new variables
        df["cases_total"] = df.eval("cases_confirmed + cases_suspected")
        df["deaths_total"] = df.eval("deaths_confirmed + deaths_suspected")
        df["positive_tests_total"] = df.eval("cases_confirmed")
        df["negative_tests_total"] = df.eval("tests_total - positive_tests_total")
        df["icu_beds_in_use_any"] = df.eval(
            "icu_beds_in_use_covid_total + icu_beds_in_use_noncovid"
        )
        df["ventilators_in_use_any"] = df.eval(
            "ventilators_in_use_covid_total + ventilators_in_use_noncovid"
        )

        # Only keep data that we want
        int_cols_to_keep = [
            "fips",
            "cases_suspected",
            "cases_confirmed",
            "cases_total",
            "deaths_suspected",
            "deaths_confirmed",
            "deaths_total",
            "positive_tests_total",
            "negative_tests_total",
            "tests_total",
            "hospital_beds_in_use_covid_total",
            "icu_beds_capacity_count",
            "icu_beds_in_use_covid_total",
            "icu_beds_in_use_any",
            "ventilators_capacity_count",
            "ventilators_in_use_covid_total",
            "ventilators_in_use_any",
        ]
        df = (
            df.loc[:, ["dt", "district_type"] + int_cols_to_keep]
            .astype({k: int for k in int_cols_to_keep})
            .query("district_type != 'd'")
        )

        # Set state-wide data fips code to Indiana's fips
        df["fips"] = df["fips"].where(df["district_type"] == "c", self.state_fips)
        df = df.drop("district_type", axis=1)

        out = df.melt(
            id_vars=["dt", "fips"], var_name="variable_name", value_name="value"
        )

        return out
