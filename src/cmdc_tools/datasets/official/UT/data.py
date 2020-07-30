import asyncio
import json
from functools import reduce
from pprint import pprint

import pandas as pd
import us

from ...base import DatasetBaseNoDate
from ...puppet import with_page
from ..base import ArcGIS


class Utah(ArcGIS, DatasetBaseNoDate):
    ARCGIS_ID = "KaHXE9OkiB9e63uE"
    has_fips = False
    state_fips = int(us.states.lookup("Utah").fips)
    source = "https://coronavirus-dashboard.utah.gov/#overview"

    def get(self):
        return self._get_overview()

    def _get_overview(self):
        df = self.get_all_sheet_to_df(
            "Utah_COVID19_Case_Counts_by_LHD_by_Day_View", sheet=0, srvid=6
        )
        renamed = df.rename(
            columns={
                "DISTNAME": "district",
                "COVID_Cases_Total": "cases_total",
                "Day": "dt",
                "Hospitalizations": "cumulative_hospitalized",
            }
        )
        renamed["dt"] = renamed["dt"].map(lambda x: pd.datetime.fromtimestamp(x / 1000))

        return (
            renamed[["dt", "district", "cases_total", "cumulative_hospitalized"]]
            .melt(id_vars=["dt", "district"], var_name="variable_name")
            .assign(vintage=pd.Timestamp.utcnow())
            .sort_values(["dt", "district"])
        )


class UtahFips(DatasetBaseNoDate):
    has_fips = True
    state_fips = int(us.states.lookup("Utah").fips)
    source = "https://coronavirus-dashboard.utah.gov/#overview"

    def get(self):
        hosp = self._get_hosp_sync()
        tests = self._get_tests_sync()

        return pd.concat([hosp, tests], sort=False)

    async def _get_hosp(self):
        url = "https://coronavirus-dashboard.utah.gov/#hospitalizations-mortality"
        async with with_page() as page:
            await page.goto(url)
            await page.waitForXPath("//div[@class='plot-container plotly']")
            plots = await page.Jx(
                "//div[@id='daily-hospital-survey-previous-8-weeks']//div[@class='plot-container plotly']/.."
            )
            text = await page.evaluate("(elem) => [elem.data, elem.layout]", plots[0])
            data = text[0]
            layout = text[1]
            reduced = self._extract_plotly_data(data, layout)

            renamed = reduced.rename(
                columns={
                    "ICU": "icu_beds_in_use_any",
                    "Non-ICU": "hospital_beds_in_use_any",
                }
            )

            return (
                renamed[["dt", "icu_beds_in_use_any", "hospital_beds_in_use_any"]]
                .melt(id_vars=["dt"], var_name="variable_name")
                .assign(vintage=pd.Timestamp.utcnow(), fips=self.state_fips)
            )

    async def _get_tests(self):
        url = "https://coronavirus-dashboard.utah.gov/#overview"

        async with with_page() as page:
            await page.goto(url)
            await page.waitForXPath("//div[@class='plot-container plotly']")
            plots = await page.Jx(
                "//div[@id='total-tests-by-date']//div[@class='plot-container plotly']/.."
            )
            text = await page.evaluate("(elem) => [elem.data, elem.layout]", plots[0])
            data = text[0]
            layout = text[1]
            # return text

            df = self._extract_plotly_data(data, layout)

            renamed = df.fillna(0)

            renamed["positive_tests_total"] = (
                renamed["Positive PCR"] + renamed["Positive Antigen"]
            ).astype(int)
            renamed["negative_tests_total"] = (
                renamed["Negative PCR"] + renamed["Negative Antigen"]
            ).astype(int)
            sorts = renamed.set_index("dt").sort_index().cumsum().reset_index()
            return (
                sorts[["dt", "negative_tests_total", "positive_tests_total"]]
                .melt(id_vars=["dt"], var_name="variable_name")
                .assign(vintage=pd.Timestamp.utcnow(), fips=self.state_fips)
            )

    def _get_hosp_sync(self):
        return asyncio.run(self._get_hosp())

    def _get_tests_sync(self):
        return asyncio.run(self._get_tests())

    def _extract_plotly_data(self, data, layout):
        dfs = []
        for trace in data:
            trace_name = trace.get("name", "")
            if trace_name == "":
                continue
            x = trace["x"]
            y = trace["y"]
            df = pd.DataFrame(data={"x": x, f"{trace_name}": y})
            df["dt"] = df.x.map(
                lambda x: (
                    pd.Timestamp(layout["xaxis"]["ticktext"][0] + " 2020")
                    + pd.Timedelta(days=(x - layout["xaxis"]["tickvals"][0]))
                )
            )
            dfs.append(df.set_index("dt"))
        return reduce(
            lambda left, right: pd.merge(left, right, on=["dt"], how="outer"), dfs,
        ).reset_index()
