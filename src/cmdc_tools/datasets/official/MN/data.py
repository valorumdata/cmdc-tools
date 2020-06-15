import pandas
import pyppeteer
import requests

from ...base import DatasetBaseNoDate


class Minnesotta(DatasetBaseNoDate):
    DAILY_URL = "https://www.health.state.mn.us/diseases/coronavirus/situation.html#dailyd1"

    def get(self):
        
        pass

    async def _get_daily_data(self):
        print("hello")
        browser = await pyppeteer.launch()
        page = await browser.newPage()
        await page.goto(self.DAILY_URL)
        daily_cases = await self._get_daily_new_cases(page)
        print("after daily cases")

    async def _get_daily_new_cases(self, page):
        text = "Newly reported cases detail"
        link = await page.Jx(f"//a/span[text()='{text}']")
        await link[0].click()
        rows = await page.Jx(f'//table[@id="dailycase"]//tr')
        # await table[0].screenshot({"path": "table.png"})
        # rows = await table[0].Jx("//tr")
        print(len(rows))
        data_rows = [] # TODO: this isn't working
        for row in rows[1:]:
            cols = await row.JJeval('td', 'elem => elem')
            print(cols)                
        return rows
        
    def _get_daily_new_deaths(self):
        pass
