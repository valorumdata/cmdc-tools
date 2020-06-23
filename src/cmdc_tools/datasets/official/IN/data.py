import pandas as pd
import requests

from ...base import DatasetBaseNoDate


class Indiana(DatasetBaseNoDate):
    def get(self):
        hosp = self._get_hosp()
        cd = self._get_case_deaths()

        return pd.concat([hosp, cd], sort=False).sort_values(["dt", "fips"])

    def _make_json_req(self):
        url = "https://www.coronavirus.in.gov/map/covid-19-indiana-daily-report-current.topojson"

        res = requests.get(url)

        return res

    def _get_case_deaths(self):
        res = self._make_json_req()
        ser = pd.Series(res.json()["objects"]["daily_statistics"])
        df = ser.to_frame().transpose()

        renamed = df.rename(
            columns={
                "total_case": "cases_confirmed",
                "total_death": "deaths_confirmed",
                "new_case_end_date": "dt",
            }
        )

        renamed.dt = pd.to_datetime(renamed.dt)
        renamed["fips"] = 18

        keep = renamed[["dt", "fips", "cases_confirmed", "deaths_confirmed"]]
        county = self._extract_county_case_deaths(res)

        result = pd.concat([keep, county], sort=False)

        return result.melt(id_vars=["dt", "fips"], var_name="variable_name")

    def _extract_county_case_deaths(self, res):
        json = res.json()["objects"]["cb_2015_indiana_county_20m"]["geometries"]
        df = pd.DataFrame.from_records([x["properties"] for x in json])
        renamed = df.rename(
            columns={
                "GEOID": "fips",
                "COVID_DEATHS": "deaths_confirmed",
                "COVID_COUNT": "cases_confirmed",
            }
        )

        renamed["dt"] = pd.to_datetime(res.json()["objects"]["update_timestamp"])

        return renamed[["dt", "fips", "deaths_confirmed", "cases_confirmed"]]

    def _get_hosp(self):
        url = "https://www.coronavirus.in.gov/map/covid-19-indiana-universal-report-current-public.json"

        res = requests.get(url)
        df = pd.DataFrame(res.json()["metrics"])

        renamed = df.rename(
            columns={
                "date": "dt",
                "district": "fips",
                "m2b_hospitalized_icu_occupied_covid": "icu_beds_in_use_covid_confirmed",
                "m2b_hospitalized_icu_supply": "icu_beds_capacity_count",
                "m2b_hospitalized_icu_occupied_non_covid": "icu_beds_in_use_any",
                "m2b_hospitalized_vent_occupied_covid": "ventilators_in_use_covid_confirmed",
                "m2b_hospitalized_vent_occupied_non_covid": "ventilators_in_use_any",
                "m2b_hospitalized_vent_supply": "ventilators_capacity_count",
            }
        )

        renamed["dt"] = pd.to_datetime(renamed["dt"])

        typed = renamed[
            [
                "dt",
                "fips",
                "district_type",
                "icu_beds_in_use_covid_confirmed",
                "icu_beds_capacity_count",
                "icu_beds_in_use_any",
                "ventilators_in_use_covid_confirmed",
                "ventilators_in_use_any",
                "ventilators_capacity_count",
            ]
        ].astype(
            {
                "icu_beds_in_use_covid_confirmed": int,
                "icu_beds_capacity_count": int,
                "icu_beds_in_use_any": int,
                "ventilators_in_use_covid_confirmed": int,
                "ventilators_in_use_any": int,
                "ventilators_capacity_count": int,
            }
        )
        # Set state-wide data fips code to Indiana's fips
        typed.loc[typed.district_type == "s", "fips"] = 18

        # Drop any district level rows
        typed = typed[typed.district_type != "d"]

        return typed[
            [
                "dt",
                "fips",
                "icu_beds_in_use_covid_confirmed",
                "icu_beds_capacity_count",
                "icu_beds_in_use_any",
                "ventilators_in_use_covid_confirmed",
                "ventilators_in_use_any",
                "ventilators_capacity_count",
            ]
        ].melt(id_vars=["dt", "fips"], var_name="variable_name")
