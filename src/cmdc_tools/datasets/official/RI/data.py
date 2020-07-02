import asyncio
import json
import os
import time

import numpy as np
import pandas as pd
import pyppeteer
import requests
import us

from ...base import DatasetBaseNoDate

# from ..base import ArcGIS
from ..base import CountyData


class RhodeIsland(DatasetBaseNoDate, CountyData):
    # ARCGIS_ID = "dkWT1XL4nglP5MLP"
    state_fips = int(us.states.lookup("Rhode Island").fips)
    has_fips = True

    # Google sheet info
    sheetid = "1n-zMS9Al94CPj_Tc3K7Adin-tN9x1RSjjx2UzJ4SV7Q"
    gsheet = f"https://docs.google.com/spreadsheets/d/{sheetid}"
    source = f"{gsheet}/edit#gid=1225599023"

    def get(self):
        state_stats = self._get_trends()
        counties = self._get_municipality()
        counties_test = self._get_citytown_testing()

        out = pd.concat(
            [state_stats, counties, counties_test],
            axis=0,
            ignore_index=True,
            sort=False,
        )
        out["vintage"] = pd.Timestamp.utcnow().normalize()

        return out

    def _get_trends(self):
        # Read data
        covid_trends = f"{self.gsheet}/export?format=csv&gid=590763272"
        df = pd.read_csv(covid_trends, parse_dates=["Date"])

        # Rename and select subset
        crename = {
            "Date": "dt",
            "Total positive labs": "positive_tests_total",
            "Total negative labs": "negative_tests_total",
            "Total tested": "tests_total",
            "Currently hospitalized": "hospital_beds_in_use_covid_total",
            "ICU": "icu_beds_in_use_covid_total",
            "Vented": "ventilators_in_use_covid_total",
            "Total deaths": "deaths_total",
        }
        df = df.rename(columns=crename).loc[:, crename.values()]
        df["fips"] = self.state_fips
        df = df.replace("--", np.NaN)

        # Melt into right shape
        out = df.melt(id_vars=["dt", "fips"], var_name="variable_name").dropna()
        out["value"] = out["value"].astype(int)

        return out

    def _get_municipality(self):
        # Read data from particular gsheet
        municipality = f"{self.gsheet}/export?format=csv&gid=1759341227"
        df = pd.read_csv(municipality)
        df = df.rename(
            columns={
                "Municipality of residence": "muni",
                "Rhode Island COVID-19 cases": "cases_total",
            }
        )

        # Prepare county/city map
        dir_path = os.path.dirname(os.path.realpath(__file__))
        county_file = f"{dir_path}/ri_citytown_to_county.json"
        with open(county_file, "r") as f:
            ct_to_c = json.load(f)

        # Map city/town into county and eliminate total and
        # those that are currently unknown
        df["fips"] = df["muni"].map(lambda x: ct_to_c.get(x, 0))
        df = df.query("fips > 0")
        df.loc[:, "cases_total"] = df.loc[:, "cases_total"].astype(int)

        # Read date from headers
        last_update = [c for c in df.columns if "update" in c][0]
        dt = pd.to_datetime(last_update.split(":")[1].strip())

        # Group by county, sum, set date time, and reshape
        df = df.loc[:, ["fips", "cases_total"]]
        counties = df.groupby("fips").agg(sum).reset_index()
        counties.loc[:, "dt"] = dt
        out = counties.melt(id_vars=["dt", "fips"], var_name="variable_name")

        return out

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
        df = pd.concat(pd.read_html(raw_table), axis=0, ignore_index=True)
        crename = {
            "City/Town": "muni",
            "Total Number of People Tested": "tests_total",
            "Number of People who Tested Positive": "positive_tests_total",
        }
        df = df.rename(columns=crename).loc[:, crename.values()]

        # Prepare county/city map
        dir_path = os.path.dirname(os.path.realpath(__file__))
        county_file = f"{dir_path}/ri_citytown_to_county.json"
        with open(county_file, "r") as f:
            ct_to_c = json.load(f)

        # Get the fips codes from our dictionary
        df["fips"] = df["muni"].map(lambda x: ct_to_c.get(x, 0))
        df = df.query("fips > 0")

        agged = (
            df.groupby("fips")[["tests_total", "positive_tests_total"]]
            .agg("sum")
            .reset_index()
        )
        agged["dt"] = pd.Timestamp.now().normalize()

        out = agged.melt(id_vars=["dt", "fips"], var_name="variable_name")

        return out
