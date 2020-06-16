import pandas as pd
import pyppeteer
import requests

from ...base import DatasetBaseNoDate


class Minnesotta(DatasetBaseNoDate):
    DAILY_URL = "https://www.health.state.mn.us/diseases/coronavirus/situation.html#dailyd1"

    async def get(self):
        browser = await pyppeteer.launch()
        page = await browser.newPage()
        await page.goto(self.DAILY_URL)
        daily = await self._get_daily_data(page)
        ts = await self._get_ts_data(page)
        result = pd.concat([daily, ts])
        return (
            result
            .melt(
                id_vars=['dt', 'county', 'fips'], 
                var_name="variable_name",
                value_name="value"
            )
        )

    async def _get_daily_data(self, page):
        daily_cases = await self._get_daily_new_cases(page)
        daily_deaths = await self._get_daily_new_deaths(page)
        result = (
            daily_cases
            .set_index('county')
            .join(daily_deaths.set_index('county'), how='left')
            .fillna(0)
        )
        result['dt'] = pd.Timestamp.utcnow().normalize()

        result.new_deaths = result.new_deaths.astype(int)
        return result.reset_index()

    async def _get_daily_new_cases(self, page):
        table = await page.Jx(f'//table[@id="dailycase"]/..')
        raw = await table[0].Jeval('table', 'node => node.outerHTML')
        s = pd.read_html(raw)
        df = pd.concat(s)
        df = df.rename(columns={
            "County": "county",
            "Number of newly reported cases": "new_cases_suspected"
        })
        return df
        
    async def _get_daily_new_deaths(self, page):
        table = await page.Jx('//table[@id="dailydeathar"]/..')
        raw = await table[0].Jeval('table', 'node => node.outerHTML')
        s = pd.read_html(raw)
        df = pd.concat(s)
        df = (
            df
            .rename(columns={
                'County of residence': "county",
                "Number of newly reported deaths": "new_deaths"
            })
            .groupby("county")
            .agg({
                "new_deaths": "sum"
            })
        )
        return df.reset_index()

    async def _get_ts_data(self, page):
        # TODO: multithread this
        testing = await self._get_testing_data(page)
        cases = await self._get_cases_table(page)
        deaths = await self._get_deaths_table(page)
        hosp = await self._get_hosp_table(page)

        result = (
            testing
            .set_index("dt")
            .join(cases.set_index("dt"), how="left")
            .join(deaths.set_index("dt"), how="left")
            .join(hosp.set_index("dt"), how="left")
            .reset_index()
        )

        result['fips'] = 27
        result.dt = result.dt + "/2020"
        result.dt = pd.to_datetime(result.dt)
        result = (
            result
            .set_index("dt")
            .tz_localize("US/Central")
            .reset_index()
        )
        return result



    async def _get_testing_data(self, page):
        table = await page.Jx("//table[@id='labtable']/..")
        raw = await table[0].Jeval('table', 'node => node.outerHTML')
        s = pd.read_html(raw, parse_dates=True)
        df = pd.concat(s)
        df = (
            df
            .rename(columns={
                "Date reported to MDH": "dt",
                "Completed tests reported from the MDH Public Health Lab (daily)": "new_tests_total_a",
                "Completed tests reported from external laboratories (daily)": "new_tests_total_b",
                "Total approximate number of completed tests": "cumulative_tests"
            })
        )

        return df
    
    async def _get_cases_table(self, page):
        table = await page.Jx("//table[@id='casetable']/..")
        raw = await table[0].Jeval('table', 'node => node.outerHTML')
        s = pd.read_html(raw, parse_dates=True)
        df = pd.concat(s)
        df = (
            df
            .rename(columns={
                "Specimen collection date": "dt",
                "Positive cases": "new_cases_confirmed",
                "Cumulative positive cases": "cumulative_cases_confirmed"
            })
        )

        return df

    async def _get_deaths_table(self, page):
        table = await page.Jx("//table[@id='deathtable']/..")
        raw = await table[0].Jeval('table', 'node => node.outerHTML')
        s = pd.read_html(raw, parse_dates=True)
        df = pd.concat(s)
        df = (
            df
            .rename(columns={
                "Date reported": "dt",
                "Newly reported deaths (daily)": "new_deaths_total",
                "Total deaths": "cumulative_deaths_total"
            })
        )

        return df

    async def _get_hosp_table(self, page):
        table = await page.Jx("//table[@id='hosptable']/..")
        raw = await table[0].Jeval('table', 'node => node.outerHTML')
        s = pd.read_html(raw, parse_dates=True)
        df = pd.concat(s)
        df = (
            df
            .rename(columns={
                "Date reported": "dt",
                "Hospitalized in ICU (daily)": "hospital_beds_in_use_covid_confirmed",
                "Hospitalized, not in ICU (daily)": "icu_beds_in_use_covid_confirmed",
                "Total hospitalizations": "cumulative_hospitalized",
                "Total ICU hospitalizations": "cumulative_icu"
            })
        )

        return df
