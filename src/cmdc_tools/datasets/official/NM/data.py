import pandas as pd
import requests
import us

from ...base import DatasetBaseNoDate
from .. import CountyData


class NewMexico(DatasetBaseNoDate, CountyData):
    source = "https://cvprovider.nmhealth.org/public-dashboard.html"
    state_fips = int(us.states.lookup("NM").fips)
    has_fips: bool = False

    def get(self):
        county = self._get_county()
        state = self._get_state()

        result = pd.concat([county, state], sort=False)

        return result.sort_values(["dt", "fips", "county"])

    def _get_county(self):
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

    def _get_state(self):
        url = "https://e7p503ngy5.execute-api.us-west-2.amazonaws.com/prod/GetPublicStatewideData"
        res = requests.get(url)
        df = pd.Series(res.json()["data"]).to_frame().T

        renamed = df.rename(
            columns={
                "created": "dt",
                "recovered": "recovered_total",
                "currentHospitalizations": "hospital_beds_in_use_covid_confirmed",
                "deaths": "deaths_total",
                "cases": "cases_total",
            }
        )
        renamed["dt"] = renamed["dt"].map(lambda x: pd.datetime.fromtimestamp(x / 1000))

        renamed["fips"] = self.state_fips
        return renamed[
            [
                "dt",
                "fips",
                "recovered_total",
                "hospital_beds_in_use_covid_confirmed",
                "deaths_total",
                "cases_total",
            ]
        ].melt(id_vars=["dt", "fips"], var_name="variable_name")
