import asyncio

import pandas as pd
import pyppeteer

from ...base import DatasetBaseNoDate
from ..base import CountyData


class Michigan(DatasetBaseNoDate, CountyData):
    def get(self):
        urls = self._get_urls()
        cases = self._get_cases(urls[0])

        return cases

    def _get_urls(self):
        urls = asyncio.run(self._get_urls_async())
        return urls

    async def _get_urls_async(self):
        browser = await pyppeteer.launch()
        page = await browser.newPage()
        await page.goto(
            "https://www.michigan.gov/coronavirus/0,9753,7-406-98163_98173---,00.html"
        )
        # get link to cases
        cases_url_raw = await page.Jx("//a[text()='Cases by County by Date']/..")
        cases_url = await cases_url_raw[0].Jeval("a", "node => node.href")
        # tests_url_raw = await page.Jx("//a[text()='COVID-19 Tests by County']/..")
        # tests_url = await tests_url_raw[0].Jeval("a", "node => node.href")

        # return [cases_url, tests_url]
        return [cases_url]

    def _get_cases(self, url):
        df = pd.read_excel(url)

        renamed = df.rename(
            columns={
                "Date": "dt",
                "COUNTY": "county",
                "Cases.Cumulative": "cases_total",
                "Deaths.Cumulative": "deaths_total",
            }
        )

        return renamed[["dt", "county", "cases_total", "deaths_total",]].melt(
            id_vars=["dt", "county"], var_name="variable_name"
        )
