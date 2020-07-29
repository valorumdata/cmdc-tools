import requests
import lxml.html
import pandas as pd
import us

from ...base import DatasetBaseNoDate
from ..base import CountyData


class Michigan(DatasetBaseNoDate, CountyData):
    """
    NOTE: Michigan does not publish test results by individual. They
          instead publish results by tests -- A single individual
          could have multiple tests
    """

    has_fips = False
    source = "https://www.michigan.gov/coronavirus/0,9753,7-406-98163_98173---,00.html"
    state_fips = int(us.states.lookup("Michigan").fips)

    def get(self):
        urls = self._get_urls()

        # Read in cases and tests
        cases_county = self._get_county_cases(urls["cases"])
        tests = self._get_tests(urls["tests"])

        result = pd.concat([cases_county, tests], sort=False, ignore_index=True, axis=0)

        return result.assign(vintage=self._retrieve_vintage())

    def _get_urls(self):
        res = requests.get(self.source)
        if not res.ok:
            raise ValueError("Error requesting html source of Michigan dashboard")
        tree = lxml.html.fromstring(res.content)

        def _get_url(link_text: str) -> str:
            path = tree.xpath(f"//a[text()='{link_text}']")[0].attrib["href"]
            return "https://www.michigan.gov" + path

        return {
            "cases": _get_url("Cases and Deaths by County"),
            "tests": _get_url("Diagnostic Tests by Result and County"),
        }

    def _get_county_cases(self, url):
        # Read excel data in
        df = pd.read_excel(url)

        # Get a consistent date format and drop other
        # date column
        df["dt"] = df["Updated"].dt.normalize()
        df = df.drop(["Updated"], axis=1).fillna(0.0)

        # Update the names of `Confirmed` and `Probable` and of
        # `Cases` and `Deaths` so that we can string concat later
        df = df.rename(
            columns={"COUNTY": "county", "Cases": "cases", "Deaths": "deaths"}
        )
        df["CASE_STATUS"] = df["CASE_STATUS"].replace(
            {"Confirmed": "confirmed", "Probable": "suspected"}
        )

        # Create new 'CASE_STATUS := Confirmed + Probable'
        totals = (
            df.groupby(["county", "dt"])
            .agg({"cases": "sum", "deaths": "sum",})
            .reset_index()
        )
        totals["CASE_STATUS"] = "total"

        # Now stack this data back into main df and reshape
        out = pd.concat([df, totals], axis=0, ignore_index=True, sort=True)
        out = out.melt(
            id_vars=["dt", "county", "CASE_STATUS"], var_name="variable"
        ).sort_values(["dt", "county", "CASE_STATUS"])
        out["variable_name"] = out["variable"] + "_" + out["CASE_STATUS"]
        out = out.drop(["CASE_STATUS", "variable"], axis=1)

        return out

    def _get_tests(self, url):
        crename = {
            "COUNTY": "county",
            "MessageDate": "dt",
            "Negative": "negative_tests_total",
            "Positive": "positive_tests_total",
            "Total": "tests_total",
        }
        df = pd.read_excel(url).rename(columns=crename)

        # Reshape so we can fill missing with 0, then reshape again to
        # prepare for cumulative sums, sort by dates, and compute
        # cumulative sums
        out = (
            df.melt(id_vars=["county", "dt"], var_name="variable_name")
            .pivot_table(
                index=["dt"], columns=["variable_name", "county"], values=["value"]
            )
            .fillna(0.0)
            .sort_index()
            .cumsum()
        )

        # Reshape to prep for entering into db
        out = out.stack(level=["county", "variable_name"]).reset_index()
        out["value"] = out["value"].astype(int)

        return out
