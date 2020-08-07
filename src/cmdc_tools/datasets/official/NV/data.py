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
        pass

    async def _get_tests_async(self):
        async with with_page(headless=False) as page:
            await page.goto(self.source)
            # Wait for dashboard to load
            await page.waitForXPath("//span[text()='COVID-19 ']")
            # Get next page button
            button = await self._get_next_page_button(page)
            print(f"Button: {button}")
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
            graph = await page.waitForXPath("//div[text()='Cumulative Tests Reported']")
            await graph.click(button="right")
            # Get table button
            table_button = await page.waitForXPath("//h6[text()='Show as a table']")
            await table_button.click()

            # get the table
            table = await page.waitForXPath(
                "//div[@class='pivotTableContainer']//div[@class='innerContainer']"
            )

            xHeader = (await self._get_table_vals(page, table, "corner"))[0]
            yHeader = (await self._get_table_vals(page, table, "columnHeaders"))[0]
            x = await self._get_table_vals(page, table, "rowHeaders")
            y = await self._get_table_vals(page, table, "bodyCells")

            print(f"Xheader: {xHeader}")
            print(f"y header: {yHeader}")
            print(f"x: {len(x)}")
            print(f"y: {len(y)}")

            data = {f"{xHeader}": x, f"{yHeader}": y}
            return data
            df = pd.DataFrame.from_dict(data)

            return df

    async def _get_next_page_button(self, page):
        # class_name = "glyphicon glyph-small pbi-glyph-chevronrightmedium middleIcon pbi-focus-outline active"
        button = await page.waitForXPath("//i[@title='Next Page']")
        return button

    async def _get_table_vals(self, page, table: ElementHandle, parentClass: str):
        xp = f"//div[@class='{parentClass}']//div[{self._class_check('pivotTableCellWrap')}]"
        elements = await table.Jx(xp)
        func = "(el) => el.textContent"
        return [(await page.evaluate(func, e)).strip() for e in elements]

    def _class_check(self, cls):
        return f"contains(concat(' ',normalize-space(@class),' '),' {cls} ')"
