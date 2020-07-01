import asyncio
import os
import time

import numpy as np
import pandas as pd
import pyppeteer
import us

from ...base import DatasetBaseNoDate

# from ..base import ArcGIS
from ..base import CountyData


class RhodeIsland(DatasetBaseNoDate, CountyData):
    # ARCGIS_ID = "dkWT1XL4nglP5MLP"
    state_fips = int(us.states.lookup("Rhode Island").fips)
    has_fips: bool = False
    source = "https://docs.google.com/spreadsheets/d/1n-zMS9Al94CPj_Tc3K7Adin-tN9x1RSjjx2UzJ4SV7Q/edit#gid=1225599023"

    def get(self):
        state_stats = self._get_trends()
        counties = self._get_municipality()
        counties_test = self._get_citytown_testing()
        return pd.concat([state_stats, counties, counties_test], sort=False)

    def _get_summary(self):
        summary_stats = "https://docs.google.com/spreadsheets/d/1n-zMS9Al94CPj_Tc3K7Adin-tN9x1RSjjx2UzJ4SV7Q/export?format=csv&gid=1225599023"
        df = pd.read_csv(summary_stats, header=None, parse_dates=True)
        df["dt"] = df.loc[0, 1]
        df = df.iloc[1:]
        renamed = df.rename(columns={0: "variable_name", 1: "value"})
        renamed = renamed.replace(
            {
                "variable_name": {
                    "Total number of positive labs received by RIDOH (cumulative count by person based on date of first positive test result)": "positive_tests_total",
                    "Total number of negative labs received by RIDOH (cumulative count by lab result)": "negative_tests_total",
                    "Number of COVID-19 cases who died in a hospital in Rhode Island (cumulative)": "hospital_deaths",
                    "Number of COVID-19 cases who are currently hospitalized in Rhode Island": "hospital_beds_in_use_covid_confirmed",
                    "Number of COVID-19 cases who are currently in an intensive care unit (ICU) in Rhode Island": "icu_beds_in_use_covid_confirmed",
                    "Number of COVID-19 cases who are currently in an intensive care unit (ICU) and on a vent in Rhode Island": "ventilators_in_use_covid_confirmed",
                }
            }
        )

        keep_rows = [
            "positive_tests_total",
            "negative_tests_total",
            "hospital_deaths",
            "hospital_beds_in_use_covid_confirmed",
            "icu_beds_in_use_covid_confirmed",
            "ventilators_in_use_covid_confirmed",
        ]
        renamed = renamed.loc[renamed.variable_name.isin(keep_rows)]
        renamed["fips"] = self.state_fips
        renamed["vintage"] = pd.Timestamp.utcnow()
        return renamed

    def _get_trends(self):
        covid_trends = "https://docs.google.com/spreadsheets/d/1n-zMS9Al94CPj_Tc3K7Adin-tN9x1RSjjx2UzJ4SV7Q/export?format=csv&gid=590763272"
        df = pd.read_csv(covid_trends, parse_dates=True)
        renamed = df.rename(
            columns={
                "Date": "dt",
                "Total positive labs": "positive_tests_total",
                "Total negative labs": "negative_tests_total",
                "Currently hospitalized": "hospital_beds_in_use_covid_confirmed",
                "ICU": "icu_beds_in_use_covid_confirmed",
                "Vented": "ventilators_in_use_covid_confirmed",
                "Total deaths": "deaths_total",
            }
        )
        renamed = renamed.replace("--", np.NaN)

        return (
            renamed[
                [
                    "dt",
                    "positive_tests_total",
                    "negative_tests_total",
                    "hospital_beds_in_use_covid_confirmed",
                    "icu_beds_in_use_covid_confirmed",
                    "ventilators_in_use_covid_confirmed",
                    "deaths_total",
                ]
            ]
            .melt(id_vars=["dt"], var_name="variable_name")
            .assign(fips=self.state_fips)
            .assign(vintage=pd.Timestamp.utcnow())
        )

    def _get_municipality(self):
        municipality = "https://docs.google.com/spreadsheets/d/1n-zMS9Al94CPj_Tc3K7Adin-tN9x1RSjjx2UzJ4SV7Q/export?format=csv&gid=1759341227"
        df = pd.read_csv(municipality)

        # Prepare county/city map
        dir_path = os.path.dirname(os.path.realpath(__file__))
        counties = pd.read_csv(f"{dir_path}/RI_counties.csv")
        counties.city = counties.city.str.upper()

        renamed = df.rename(
            columns={
                "Municipality of residence": "muni",
                "Rhode Island COVID-19 cases": "cases_total",
            }
        )

        renamed.muni = renamed.muni.str.upper()

        joined = (
            renamed.set_index("muni")
            .join(counties.set_index("city"), how="left")
            .reset_index()
        )
        filtered = joined.loc[joined.county.isin(list(counties.county))]
        filtered = filtered[["county", "cases_total"]]
        filtered.cases_total = filtered.cases_total.astype(int)
        agged = filtered.groupby("county").agg(sum).reset_index()
        agged["dt"] = pd.Timestamp.utcnow()
        return agged.melt(id_vars=["dt", "county"], var_name="variable_name").assign(
            vintage=pd.Timestamp.utcnow()
        )

    async def _get_table_async(self):
        browser = await pyppeteer.launch()
        page = await browser.newPage()
        await page.goto("https://datawrapper.dwcdn.net/udDUY/4/")
        graphHeader = "Number of People COVID-19 Tested and Number of People with Positive Tests in Rhode Island Cities and Towns"
        # wait for table to load
        await page.waitForXPath("//table")
        # Get raw html of table
        raw_table = await page.Jeval("table", "el => el.outerHTML")
        return raw_table

    def _get_table(self):
        return asyncio.run(self._get_table_async())

    def _get_citytown_testing(self):
        raw_table = self._get_table()

        df = pd.concat(pd.read_html(raw_table))
        # Prepare county list
        dir_path = os.path.dirname(os.path.realpath(__file__))
        counties = pd.read_csv(f"{dir_path}/RI_counties.csv")
        counties.city = counties.city.str.upper()

        df["City/Town"] = df["City/Town"].str.upper()

        joined = (
            df.set_index("City/Town")
            .join(counties.set_index("city"), how="left")
            .reset_index()
        )

        renamed = joined.rename(
            columns={
                "Total Number of People Tested": "tests_total",
                "Number of People who Tested Positive": "positive_tests_total",
            }
        )
        agged = (
            renamed[["county", "tests_total", "positive_tests_total"]]
            .groupby("county")
            .agg(sum)
        ).reset_index()
        return (
            agged.melt(id_vars=["county"], var_name="variable_name")
            .assign(vintage=pd.Timestamp.utcnow().normalize())
            .assign(dt=pd.Timestamp.utcnow())
        )

    # NOTE: This set of code is used for Rhode Island's ArcGIS server. It is currently
    # in testing and the data is fake. Once it is running, we can use this code
    # def _get(self):
    #     df = self.get_all_sheet_to_df(service="COVID_Public_Map_TEST", sheet=2, srvid=1)

    #     df.Date = df.Date.fillna(int(time.time()))

    #     df.Date = pd.to_datetime(
    #         df.Date.map(lambda x: pd.datetime.fromtimestamp(x / 1000).date())
    #     )
    #     dir_path = os.path.dirname(os.path.realpath(__file__))
    #     counties = pd.read_csv(f"{dir_path}/RI_counties.csv")
    #     counties.city = counties.city.str.upper()
    #     cols = {
    #         "Count_of_COVID_19_Positive": "cases_confirmed",  # cumulativeff
    #         "Covid_Deaths": "deaths_confirmed",  # cumulative
    #         "Covid_ICU": "icu_beds_in_use_covid_confirmed",  # daily
    #         "Covid_Ventilator": "ventilators_in_use_covid_confirmed",
    #         "Total_Covid_Lab_Tests": "total_tests",  # cumulative
    #         "Negative_Covid_Lab_Tests": "negative_tests_total",  # cumulative
    #         "City_Town": "city",
    #         "Date": "dt",  # TODO: Dates are all 2020-04-07. wtf?
    #     }
    #     return df
    #     renamed = df.rename(columns=cols)

    #     renamed["positive_tests_total"] = (
    #         renamed.total_tests - renamed.negative_tests_total
    #     )
    #     keep_cols = list(cols.values())
    #     keep_cols.append("positive_tests_total")
    #     renamed = renamed[keep_cols]
    #     renamed.city = renamed.city.str.upper()
    #     # Join county name
    #     joined = renamed.set_index("city").join(counties.set_index("city"), how="left")
    #     return joined
    #     jgb = joined.reset_index().groupby("county")
    #     result = jgb.agg(
    #         {
    #             "cases_confirmed": "sum",
    #             "deaths_confirmed": "max",
    #             "icu_beds_in_use_covid_confirmed": "max",
    #             "ventilators_in_use_covid_confirmed": "max",
    #             "total_tests": "max",
    #             "negative_tests_total": "max",
    #             "dt": "max",
    #         }
    #     )
    #     return (
    #         result.reset_index()
    #         .melt(id_vars=["dt", "county"], var_name="variable_name")
    #         .assign(vintage=pd.Timestamp.utcnow().normalize())
    #     )
