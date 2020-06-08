import asyncio
import numpy as np
import pandas as pd

from ..base import CountyData
from ...puppet import with_page

from pyppeteer.element_handle import ElementHandle


async def get_data_from_pivot_table(el):
    pass


def _class_check(cls):
    return f"contains(concat(' ',normalize-space(@class),' '),' {cls} ')"


async def _get_table_vals(page, table: ElementHandle, parentClass: str):
    xp = f"//div[@class='{parentClass}']//div[{_class_check('pivotTableCellWrap')}]"
    elements = await table.Jx(xp)
    func = "(el) => el.textContent"
    return [(await page.evaluate(func, e)).strip() for e in elements]


async def main():
    async with with_page() as page:
        await page.goto(
            "https://app.powerbi.com/view?r=eyJrIjoiYjU5MzU4NjAtZWJjMC00MTllLTkwYjYtMzE4ODY1YjAyMGU2IiwidCI6ImI3MjgwODdjLTgwZTgtNGQzMS04YjZmLTdlMGUzYmUxMGUwOCIsImMiOjN9"
        )
        await (
            await page.waitForXPath("//span[text()='Hospital/COVID Census']/..")
        ).click()
        await (await page.waitForXPath("//div[@aria-label='Harris']")).click()
        await (await page.JJ("div.visual-lineChart"))[0].click(
            options={"button": "right"}
        )

        tableButton = await page.waitForXPath(
            "//drop-down-list-item[//h6[text()='Show as a table']]",
            options=dict(visible=True),
        )

        await tableButton.click()

        table = await page.waitForXPath("//div[@aria-label='Grid']")

        colnames = await _get_table_vals(page, table, "columnHeaders")
        raw_data = np.array(
            await _get_table_vals(page, table, "bodyCells"), dtype="int", order="F"
        )
        index = pd.to_datetime(await _get_table_vals(page, table, "rowHeaders"))

    out = pd.DataFrame(
        raw_data.reshape((-1, len(colnames)), order="F"), index=index, columns=colnames
    )

    colmap = {
        "Patients in General Beds (Suspected + Confirmed)": "hospital_count",
        "Patients in Intensive Care Beds (Suspected + Confirmed)": "icu_count",
        "Total Hospital Patient Census": "total_hospital_count",
    }

    return out.rename(columns=colmap)


# asyncio.run(main())
