import asyncio
import glob
import os
import tempfile

import pandas as pd

from ...puppet import with_page, xpath_class_check


async def test_data():
    with tempfile.TemporaryDirectory() as tmpdirname:
        print("this is the tmpdir:", tmpdirname)
        async with with_page(headless=True) as page:
            await page.goto(
                "https://app.powerbigov.us/view?r=eyJrIjoiYzI3NjYwYjEtZTNhMi00NzE0LTk0ODYtNjJkYzZjMzg0YTYxIiwidCI6IjExZDBlMjE3LTI2NGUtNDAwYS04YmEwLTU3ZGNjMTI3ZDcyZCJ9",
                {"waitUntil": "networkidle2"},
            )
            resp = await page._client.send(
                "Page.setDownloadBehavior",
                {"behavior": "allow", "downloadPath": tmpdirname},
            )
            print("here's what chrome said:", resp)

            button = await page.waitForXPath(
                "//button/span[contains(text(), 'Testing')]/.."
            )
            print("I have this button!", button)
            await button.click()

            download = await page.waitForXPath(
                "//button/span[contains(text(), 'Download')]/.."
            )
            await download.click()

            for _ in range(10):
                fns = glob.glob(os.path.join(tmpdirname, "*.xlsx"))
                if len(fns) == 1:
                    break
                await asyncio.sleep(1)
            else:
                print("well poop")
                await asyncio.sleep(10)
                raise ValueError("Couldn't wait long enough for the file")

            df = pd.read_excel(fns[0])

    return df


def main():
    return asyncio.run(test_data())
