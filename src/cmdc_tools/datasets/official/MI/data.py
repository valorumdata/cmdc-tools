import asyncio

import pandas as pd
import pyppeteer
import us

from ...base import DatasetBaseNoDate
from ..base import CountyData


class Michigan(DatasetBaseNoDate, CountyData):
    has_fips = False
    source = "https://www.michigan.gov/coronavirus/0,9753,7-406-98163_98173---,00.html"
    state_fips = int(us.states.lookup("Michigan").fips)

    def get(self):
        urls = self._get_urls()
        cases = self._get_cases(urls[0])
        cases_county = self._get_county_cases(urls[1])
        tests = self._get_tests(urls[2])
        result = pd.concat([cases, cases_county, tests], sort=False)
        return result

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
        cases_county_url_raw = await page.Jx(
            "//a[text()='Cases and Deaths by County']/.."
        )
        cases_county_url = await cases_county_url_raw[0].Jeval("a", "node => node.href")
        tests_url_raw = await page.Jx(
            "//a[text()='Diagnostic Tests by Result and County']/.."
        )
        tests_url = await tests_url_raw[0].Jeval("a", "node => node.href")

        return [cases_url, cases_county_url, tests_url]
        # return [cases_url]

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

    def _get_county_cases(self, url):
        df = pd.read_excel(url)

        confirmed = df.loc[df.CASE_STATUS == "Confirmed"]
        confirmed = confirmed.rename(
            columns={
                "Updated": "dt",
                "COUNTY": "county",
                "Cases": "cases_confirmed",
                "Deaths": "deaths_confirmed",
            }
        )[["dt", "county", "cases_confirmed", "deaths_confirmed"]]

        probable = df.loc[df.CASE_STATUS == "Probable"]
        probable = probable.rename(
            columns={
                "Updated": "dt",
                "COUNTY": "county",
                "Cases": "cases_suspected",
                "Deaths": "deaths_suspected",
            }
        )[["dt", "county", "cases_suspected", "deaths_suspected"]]

        result = (
            confirmed.set_index(["dt", "county"])
            .join(probable.set_index(["dt", "county"]))
            .reset_index()
        )

        return result.fillna(0).melt(id_vars=["dt", "county"], var_name="variable_name")

    def _get_tests(self, url):
        df = pd.read_excel(url)
        renamed = df.rename(
            columns={
                "COUNTY": "county",
                "MessageDate": "dt",
                "Negative": "negative_tests_total",
                "Positive": "positive_tests_total",
            }
        )

        return renamed[
            ["county", "dt", "negative_tests_total", "positive_tests_total",]
        ].melt(id_vars=["dt", "county"], var_name="variable_name")
