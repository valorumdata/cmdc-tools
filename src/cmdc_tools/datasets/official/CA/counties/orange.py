import pandas as pd
import requests
import us

from .... import DatasetBaseNoDate
from ... import ArcGIS


class CAOrange(DatasetBaseNoDate, ArcGIS):
    """
    Orange publishes their county level data in a dashboard that can
    be found at:

    https://occovid19.ochealthinfo.com/coronavirus-in-oc
    """

    ARCGIS_ID = "LORzk2hk9xzHouw9"
    source = (
        "https://ochca.maps.arcgis.com/apps/opsdashboard/index.html"
        "#/cc4859c8c522496b9f21c451de2fedae"
    )
    county_fips = 59  # 06059 - Orange County, CA
    state_fips = int(us.states.lookup("California").fips)
    has_fips = True
    provider = "county"

    def _get_tests(self):
        crename = {
            "date": "dt",
            "tot_spec": "tests_total",
            "tot_pcr_pos": "positive_tests_total"
        }
        df = self.get_all_sheet_to_df("occovid_pcr_csv", 0, 2)
        df = df.rename(columns=crename).loc[:, crename.values()]

        df["fips"] = 1000*self.state_fips + self.county_fips
        df["dt"] = df["dt"].map(lambda x: self._esri_ts_to_dt(x))
        df["negative_tests_total"] = df.eval(
            "tests_total - positive_tests_total"
        )

        out = df.melt(id_vars=["dt", "fips"], var_name="variable_name")
        out["vintage"] = self._retrieve_vintage()

        # Final clean up
        out = out.dropna().sort_values(["dt"])
        out["value"] = out["value"].astype(int)

        return out

    def get(self):

        tests = self._get_tests()
        out = pd.concat([tests,], axis=0, ignore_index=True, sort=True)

        return out
