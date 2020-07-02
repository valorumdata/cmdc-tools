import requests
import lxml.html
import pandas as pd
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
        return result.assign(vintage=pd.Timestamp.utcnow().normalize())

    def _get_urls(self):
        res = requests.get(self.source)
        if not res.ok:
            raise ValueError("Error requesting html source of Michigan dashboard")
        tree = lxml.html.fromstring(res.content)

        def _get_url(link_text: str) -> str:
            path = tree.xpath(f"//a[text()='{link_text}']")[0].attrib["href"]
            return "https://www.michigan.gov" + path

        cases_url = _get_url("Cases by County by Date")
        tests_url = _get_url("Diagnostic Tests by Result and County")
        cases_county_url = _get_url("Cases and Deaths by County")

        return [cases_url, cases_county_url, tests_url]

    def _get_cases(self, url):
        column_names = {
            "Date": "dt",
            "COUNTY": "county",
            "Cases.Cumulative": "cases_total",
            "Deaths.Cumulative": "deaths_total",
        }
        return (
            pd.read_excel(url)
            .rename(columns=column_names)
            .loc[:, list(column_names.values())]
            .melt(id_vars=["dt", "county"], var_name="variable_name")
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
        column_names = {
            "COUNTY": "county",
            "MessageDate": "dt",
            "Negative": "negative_tests_total",
            "Positive": "positive_tests_total",
        }
        return (
            pd.read_excel(url)
            .rename(columns=column_names)
            .loc[:, list(column_names.values())]
            .melt(id_vars=["dt", "county"], var_name="variable_name")
        )
