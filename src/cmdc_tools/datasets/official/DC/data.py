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
        await page.goto("https://coronavirus.dc.gov/page/coronavirus-data")
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
        renamed = df.rename(columns={"Unnamed: 1": "Feature"})
        dropped = renamed.drop(columns=["Unnamed: 0"])
        trans = dropped.set_index("Feature").T
        renamed = trans.rename(
            columns={
                "Total Overall Tested": "tests_total",
                "Total Positives": "positive_tests_total",
                "Number of Deaths": "deaths_total",
                "ICU Beds Available": "icu_beds_available",
                "Total Reported Ventilators in Hospitals": "ventilator_capacity_count",
                "In-Use Ventilators in Hospitals": "ventilators_in_use_any",
                "Total COVID-19 Patients in DC Hospitals": "hospital_beds_in_use_covid_confirmed",
                "Total COVID-19 Patients in ICU": "icu_beds_in_use_covid_confirmed",
                "Total Patients in DC Hospitals (COVID and non-COVID": "hospital_beds_in_use_any",
                "Total Number Recovered": "recovered_total",
            }
        )
        renamed["fips"] = self.state_fips
        return (
            renamed[
                [
                    "fips",
                    "tests_total",
                    "positive_tests_total",
                    "deaths_total",
                    "icu_beds_available",
                    "ventilator_capacity_count",
                    "ventilators_in_use_any",
                    "hospital_beds_in_use_covid_confirmed",
                    "icu_beds_in_use_covid_confirmed",
                    "hospital_beds_in_use_any",
                    "recovered_total",
                ]
            ]
            .reset_index()
            .rename(columns={"index": "dt"})
            .melt(id_vars=["dt", "fips"], var_name="variable_name")
        )
