import pandas as pd
import requests
import us

from .. import CountyData
from ...base import DatasetBaseNoDate


class NewMexico(DatasetBaseNoDate, CountyData):
    source = "https://cvprovider.nmhealth.org/public-dashboard.html"
    state_fips = int(us.states.lookup("NM").fips)

    def get(self):
        url = "https://e7p503ngy5.execute-api.us-west-2.amazonaws.com/prod/GetCounties"
        res = requests.get(url)

        df = pd.DataFrame(res.json()["data"])

        renamed = df.rename(
            columns={
                "name": "county",
                "cases": "cases_total",
                "deaths": "deaths_total",
                "created": "dt",
                "recovered": "recovered_total",
            }
        )
        renamed["dt"] = renamed["dt"].map(lambda x: pd.datetime.fromtimestamp(x / 1000))
        return renamed[
            ["dt", "county", "cases_total", "deaths_total", "recovered_total",]
        ].melt(id_vars=["dt", "county"], var_name="variable_name")
