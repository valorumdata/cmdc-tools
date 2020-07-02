import pandas as pd
import requests
import us

from ...base import DatasetBaseNoDate
from .. import CountyData


class NewMexico(DatasetBaseNoDate, CountyData):
    source = "https://cvprovider.nmhealth.org/public-dashboard.html"
    state_fips = int(us.states.lookup("NM").fips)
    has_fips: bool = True

    def get(self):
        return pd.concat(
            [self._get_county(), self._get_state()], ignore_index=True, sort=False
        )

    def _get_county(self):
        url = "https://e7p503ngy5.execute-api.us-west-2.amazonaws.com/prod/GetCounties"
        res = requests.get(url)

        df = pd.DataFrame(res.json()["data"])

        column_names = {
            "countyId": "fips",
            "cases": "cases_total",
            "deaths": "deaths_total",
            "created": "dt",
            "recovered": "recovered_total",
            "tests": "tests_total",
        }

        renamed = df.rename(columns=column_names)
        renamed["fips"] = renamed["fips"] + self.state_fips * 1000
        renamed["dt"] = renamed["dt"].map(lambda x: pd.datetime.fromtimestamp(x / 1000))
        return renamed.loc[:, list(column_names.values())].melt(
            id_vars=["dt", "fips"], var_name="variable_name"
        )

    def _get_state(self):
        url = "https://e7p503ngy5.execute-api.us-west-2.amazonaws.com/prod/GetPublicStatewideData"
        res = requests.get(url)
        df = pd.Series(res.json()["data"]).to_frame().T

        column_names = {
            "created": "dt",
            "recovered": "recovered_total",
            "currentHospitalizations": "hospital_beds_in_use_covid_total",
            "deaths": "deaths_total",
            "cases": "cases_total",
            "tests": "tests_total",
        }

        renamed = df.rename(columns=column_names)
        renamed["dt"] = renamed["dt"].map(lambda x: pd.datetime.fromtimestamp(x / 1000))

        renamed["fips"] = self.state_fips
        return renamed.loc[:, ["fips"] + list(column_names.values())].melt(
            id_vars=["dt", "fips"], var_name="variable_name"
        )
