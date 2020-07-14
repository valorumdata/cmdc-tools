import asyncio
import glob
import io
import os
import tempfile
from cmdc_tools.datasets.puppet import with_page

import pandas as pd


async def get_file():
    async with with_page(headless=True) as page:
        await page.goto(
            "https://bi.ahca.myflorida.com/t/ABICC/views/Public/ICUBedsHospital?:isGuestRedirectFromVizportal=y&:embed=y"
        )

        with tempfile.TemporaryDirectory() as tmpdirname:
            await page._client.send(
                "Page.setDownloadBehavior",
                {"behavior": "allow", "downloadPath": tmpdirname},
            )
            await page.waitForSelector(".tabCanvas")
            table = await page.waitForSelector(".tabCanvas")
            print(table)
            await table.click()

            # TODO: better way to ensure click happened? Perhaps check css class for cell highlighting?
            for i in range(4):
                print("attempt ", i)
                await asyncio.sleep(2)
                await page.mouse.click(570, 477, options={"delay": 100})

            button = await page.waitForSelector("#download-ToolbarButton")
            await button.click()
            crosstab = await page.waitForXPath(
                "//button[@data-tb-test-id = 'DownloadCrosstab-Button']"
            )
            await crosstab.click()

            # TODO: better way to wait for download?
            await asyncio.sleep(5)
            fns = glob.glob(os.path.join(tmpdirname, "*.csv"))
            assert len(fns) == 1
            print(fns[0])
            with open(fns[0], "rb") as f:
                tsv = io.BytesIO(f.read().decode("UTF-16").encode("UTF-8"))
                df = pd.read_csv(tsv, sep="\t")

    return df


def main():
    df = asyncio.run(get_file())
    str_cols = ["County", "FileNumber", "ProviderName"]
    for col in list(df):
        for bad in (r",", r"%", "nan"):
            df[col] = df[col].astype(str).str.replace(bad, "")
        if col not in str_cols:
            df[col] = pd.to_numeric(df[col])

    return df
