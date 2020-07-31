import requests
import textwrap

import pandas as pd
import us

from ..base import CountyData
from ... import DatasetBaseNoDate


class CACountyData(DatasetBaseNoDate, CountyData):
    source = "https://public.tableau.com/profile/ca.open.data#!/vizhome/COVID-19HospitalsDashboard/Hospitals"
    state_fips = int(us.states.lookup("California").fips)
    has_fips = False
    query_url = "https://data.ca.gov/api/3/action/datastore_search"

    def data_from_api(self, resource_id, limit=1000, **kwargs):
        # Create values needed for iterating
        offset = 0
        nrecords = 0
        params = dict(resource_id=resource_id, limit=limit, offset=offset, **kwargs)

        dfs = []
        keep_requesting = True
        while keep_requesting:
            res = requests.get(self.query_url, params=params).json()
            if not res["success"]:
                raise ValueError("The request open CA data request failed...")

            records = res["result"]["records"]
            offset += len(records)
            keep_requesting = offset < res["result"]["total"]

            dfs.append(pd.DataFrame(records))
            params.update(dict(offset=offset))

        out = pd.concat(dfs, axis=0, ignore_index=True)

        return out

    def get(self):
        cd_df = self.get_case_death_data()
        hosp_df = self.get_hospital_data()
        test_df = self.get_test_data()

        df = pd.concat(
            [cd_df, hosp_df, test_df], axis=0, ignore_index=True, sort=True
        )
        df["value"] = df["value"].astype(int)
        df["vintage"] = pd.Timestamp.utcnow().normalize()

        return df

    def get_case_death_data(self):
        resource_id = "926fd08f-cc91-4828-af38-bd45de97f8c3"
        df = self.data_from_api(resource_id=resource_id)

        # Rename columns and subset data
        crename = {
            "date": "dt",
            "county": "county",
            "totalcountconfirmed": "cases_total",
            "totalcountdeaths": "deaths_total",
        }
        df = df.rename(columns=crename).loc[:, crename.values()]
        df["dt"] = pd.to_datetime(df["dt"])

        # Reshape
        out = df.melt(
            id_vars=["dt", "county"], var_name="variable_name", value_name="value"
        ).dropna()

        return out

    def get_hospital_data(self):
        # Get url for download
        resource_id = "42d33765-20fd-44b8-a978-b083b7542225"
        df = self.data_from_api(resource_id=resource_id)

        # Rename columns and subset data
        crename = {
            "todays_date": "dt",
            "county": "county",
            "hospitalized_covid_confirmed_patients": "hospital_beds_in_use_covid_confirmed",
            "hospitalized_suspected_covid_patients": "hospital_beds_in_use_covid_suspected",
            "hospitalized_covid_patients": "hospital_beds_in_use_covid_total",
            "all_hospital_beds": "hospital_beds_capacity_count",
            "icu_covid_confirmed_patients": "icu_beds_in_use_covid_confirmed",
            "icu_suspected_covid_patients": "icu_beds_in_use_covid_suspected",
            # "icu_available_beds": "icu_beds_capacity_count", Unsure if this is capacity
        }
        df = df.rename(columns=crename).loc[:, crename.values()]

        # Convert to numeric and date
        df = df.replace("None", None)
        df = df.apply(lambda x: pd.to_numeric(x, errors="ignore"))
        df["dt"] = pd.to_datetime(df["dt"])

        df["icu_beds_in_use_covid_total"] = df.eval(
            "icu_beds_in_use_covid_confirmed + icu_beds_in_use_covid_suspected"
        )

        # Reshape
        out = df.melt(
            id_vars=["dt", "county"], var_name="variable_name", value_name="value"
        ).dropna()
        out["value"] = out["value"].astype(int)

        return out

    def get_test_data(self):
        resource_id = "b6648a0d-ff0a-4111-b80b-febda2ac9e09"
        df = self.data_from_api(resource_id=resource_id)

        df = df.rename(columns={"date": "dt", "tested": "tests_total",}).drop(
            "_id", axis=1
        )
        df["dt"] = pd.to_datetime(df["dt"])
        df["fips"] = self.state_fips

        out = df.melt(id_vars=["dt", "fips"], var_name="variable_name")

        return out
