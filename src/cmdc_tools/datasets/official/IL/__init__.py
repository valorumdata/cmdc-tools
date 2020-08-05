import pandas as pd
import requests
import us

from ...base import DatasetBaseNoDate
from ..base import CountyData


class Illinois(DatasetBaseNoDate, CountyData):
    has_fips = False
    source = "https://www.dph.illinois.gov/covid19/covid19-statistics"
    state_fips = int(us.states.lookup("Illinois").fips)

    def get(self):
        url = "https://www.dph.illinois.gov/sitefiles/COVIDHistoricalTestResults.json?nocache=1"

        res = requests.get(url)
        if not res.ok:
            raise ValueError("Could not request data")

        js = res.json()
        column_names = {
            "County": "county",
            "confirmed_cases": "cases_total",
            "deaths": "deaths_total",
            "total_tested": "tests_total",
        }

        to_cat = []
        for date_data in js["historical_county"]["values"]:
            dt = pd.to_datetime(date_data["testDate"])
            to_cat.append(
                pd.DataFrame(date_data["values"])
                .rename(columns=column_names)
                .loc[:, list(column_names.values())]
                .assign(dt=dt)
            )

        df = pd.concat(to_cat, ignore_index=True, sort=True)
        df["vintage"] = self._retrieve_vintage()

        out = df.melt(id_vars=["dt", "county", "vintage"], var_name="variable_name")

        return out.drop_duplicates(subset=["dt", "county", "variable_name", "vintage"])
