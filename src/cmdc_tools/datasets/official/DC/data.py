import asyncio
import io

import pandas as pd
import pyppeteer
import requests
import us

from ...base import DatasetBaseNoDate
from ..base import CountyData


class DC(DatasetBaseNoDate, CountyData):
    has_fips = True
    state_fips = int(us.states.lookup("DC").fips)
    source = "https://coronavirus.dc.gov/page/coronavirus-data"

    def _get_urls(self):
        link = asyncio.run(self._get_urls_async())
        return link

    async def _get_urls_async(self):
        browser = await pyppeteer.launch()
        page = await browser.newPage()
        await page.goto(self.source)
        link_raw = await page.Jx("//a[text()='Download copy of DC COVID-19 data']/..")
        link = await link_raw[0].Jeval("a", "node => node.href")
        # Navigate to link

        return link

    def _get_df(self):
        url = self._get_urls()
        res = requests.get(url)
        with io.BytesIO(res.content) as fh:
            df = pd.io.excel.read_excel(fh)
            return df

    def get(self):
        df = self._get_df()
        df = df.rename(
            columns={"Unnamed: 1": "variable_name"}
        ).drop(
            "Unnamed: 0", axis=1
        )

        # Rename and only keep relevant data
        vrename = {
            # Case/Death/Tests
            "Total Positives": "cases_total",
            "Number of Deaths": "deaths_total",
            "Total Overall Tested": "tests_total",
            "Total Number Recovered": "recovered_total",
            # ICU
            "Total ICU Beds in Hospitals": "icu_beds_capacity_count",
            "ICU Beds Available": "icu_beds_available",
            "Total COVID-19 Patients in ICU": "icu_beds_in_use_covid_total",
            # Hospitals
            "Total Patients in DC Hospitals (COVID and non-COVID": "hospital_beds_in_use_any",
            "Total Patients in DC Hospitals (COVID and non-COVID)": "hospital_beds_in_use_any",
            "Total COVID-19 Patients in DC Hospitals": "hospital_beds_in_use_covid_total",
            # Ventilators
            "Total Reported Ventilators in Hospitals": "ventilator_capacity_count",
            "In-Use Ventilators in Hospitals": "ventilators_in_use_any",
        }
        df = df.query("variable_name in @vrename.keys()")
        df["variable_name"] = df["variable_name"].replace(vrename)

        # Move date from columns to rows
        df = df.melt(id_vars="variable_name", var_name="dt").dropna()
        df["value"] = df["value"].astype(int)
        df["fips"] = self.state_fips
        df["vintage"] = pd.Timestamp.utcnow().normalize()

        return df
