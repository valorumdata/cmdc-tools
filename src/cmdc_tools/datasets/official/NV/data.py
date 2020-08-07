import asyncio

import pandas as pd
import us
from pyppeteer.element_handle import ElementHandle

from ...base import DatasetBaseNoDate
from ...puppet import with_page


class Nevada(DatasetBaseNoDate):
    state_fips = int(us.states.lookup("Nevada").fips)
    has_fips = False
    source = "https://app.powerbigov.us/view?r=eyJrIjoiMjA2ZThiOWUtM2FlNS00MGY5LWFmYjUtNmQwNTQ3Nzg5N2I2IiwidCI6ImU0YTM0MGU2LWI4OWUtNGU2OC04ZWFhLTE1NDRkMjcwMzk4MCJ9"

    def get(self):
        cases = self._get_cases()
        tests = self._get_tests()
        return pd.concat([tests, cases], sort=False)

    def _get_tests(self):
        return asyncio.run(self._get_tests_async())

    def _get_cases(self):
        return asyncio.run(self._get_cases_async())

    async def _get_tests_async(self):
        async with with_page() as page:
            await page.goto(self.source)
            # Wait for dashboard to load
            await page.waitForXPath("//span[text()='COVID-19 ']")
            # Get next page button
            button = await self._get_next_page_button(page)
            await button.click()
            # Wait for dashboard to load
            await page.waitForXPath("//div[text()='COVID-19 Statistics by County']")
            # Go to next page
            await button.click()
            # Wait for dashboard to laod
            await page.waitForXPath("//div[text()='Results Filter for Demographics']")
            # Go to next page
            await button.click()
            # Find cumulative tests reported graph
            graph = await page.waitForXPath("//*[@class='cartesianChart']")
            await graph.click(button="right")
            # Get table button
            table_button = await page.waitForXPath("//h6[text()='Show as a table']")
            await table_button.click()

            labels = await self._get_labels_from_graph(page)

            # parse labels
            data = []
            for label in labels:
                split = label.split(". ")
                date = split[0].split("Date")[1].strip() + "/2020"
                tests = split[1].split("Tests")
                tests_type = tests[0].strip()
                # Skip all new tests
                if tests_type == "New":
                    break
                tests_num = int(tests[1][:-1].strip().replace(",", ""))
                {"Date": date, f"{tests_type}": tests_num}
                data.append({"Date": date, f"{tests_type}": tests_num})

            df = pd.DataFrame(data)
            renamed = df.rename(columns={"Date": "dt", "Cumulative": "tests_total"})
            renamed.dt = pd.to_datetime(renamed.dt)
            return renamed.melt(id_vars=["dt"], var_name="variable_name").assign(
                vintage=pd.Timestamp.utcnow(), fips=self.state_fips
            )

    async def _get_labels_from_graph(self, page):
        # wait for graph to load
        visual_modern = await page.waitForXPath("//*[@class='cartesianChart']")
        # get all graph points
        elems = await visual_modern.Jx(
            "//*[@class='series']//*[@class='column setFocusRing']"
        )

        labels = [
            (await page.evaluate("(el) => el.getAttribute('aria-label')", e))
            for e in elems
        ]

        return labels

    async def _get_cases_async(self):
        async with with_page() as page:
            await page.goto(self.source)
            # Wait for dashboard to load
            # Get next page button
            await page.waitForXPath("//span[text()='COVID-19 ']")
            button = await self._get_next_page_button(page)
            await button.click()
            # Wait for dashboard to load
            # Go to next page
            await page.waitForXPath("//div[text()='COVID-19 Statistics by County']")
            await button.click()
            # Wait for dashboard to laod
            # Go to next page
            await page.waitForXPath("//div[text()='Results Filter for Demographics']")
            await button.click()

            await page.waitForXPath("//div[text()='Cumulative Tests Reported']")
            await button.click()

            # Find cumulative cases reported graph
            graph = await page.waitForXPath("//*[@class='cartesianChart']")
            await graph.click(button="right")
            # Get table button
            table_button = await page.waitForXPath("//h6[text()='Show as a table']")
            await table_button.click()

            labels = await self._get_labels_from_graph(page)

            # parse labels
            data = []
            for label in labels:
                split = label.split(". ")
                date = split[0].split("Date")[1].strip() + "/2020"
                tests = split[1].split(" ")
                tests_type = tests[0].strip()
                # Skip all new tests
                if tests_type == "New":
                    break
                tests_num = int(tests[1][:-1].strip().replace(",", ""))
                {"Date": date, f"{tests_type}": tests_num}
                data.append({"Date": date, f"{tests_type}": tests_num})

            df = pd.DataFrame(data)
            renamed = df.rename(columns={"Date": "dt", "Cases": "cases_total"})
            renamed.dt = pd.to_datetime(renamed.dt)
            return renamed.melt(id_vars=["dt"], var_name="variable_name").assign(
                vintage=pd.Timestamp.utcnow(), fips=self.state_fips
            )

    async def _get_next_page_button(self, page):
        # class_name = "glyphicon glyph-small pbi-glyph-chevronrightmedium middleIcon pbi-focus-outline active"
        button = await page.waitForXPath("//i[@title='Next Page']")
        return button
