import asyncio

import bs4
import pandas as pd
import us

from ...puppet import with_page
from ... import DatasetBaseNoDate
from .. import CountyData


class Washington(DatasetBaseNoDate, CountyData):
    source = "https://www.doh.wa.gov/Emergencies/COVID19/DataDashboard"
    state_fips = int(us.states.lookup("Washington").fips)
    has_fips = False
    url = "https://www.doh.wa.gov/Emergencies/COVID19/DataDashboard"

    def get(self) -> pd.DataFrame:
        return asyncio.run(self._get_data())

    async def _get_data(self):
        async with with_page(headless=True) as page:
            await page.goto(
                "https://www.doh.wa.gov/Emergencies/COVID19/DataDashboard",
                {"waitUntil": "networkidle2"},
            )

        res = await page.content()

        soup = bs4.BeautifulSoup(res)
        tables = soup.select("#pnlConfirmedCasesDeathsTbl table")
        assert len(tables) == 1
        dfs = pd.read_html(str(tables[0]))
        assert len(dfs) == 1
        df = (
            dfs[0].query("County not in  ('Unassigned', 'Total')")
            .rename(columns={
                "County": "county",
                "Confirmed Cases": "cases_total",
                "Hospitalizations": "hospital_beds_in_use_covid_total",
                "Deaths": "deaths_total",
            })
            .assign(
                vintage=self._retrieve_vintage(),
                dt=self._retrieve_dt(tz="US/Pacific")
            )
            .melt(
                id_vars=["vintage", "dt", "county"],
                var_name="variable_name",
                value_name="value"
            )
        )
        return df
