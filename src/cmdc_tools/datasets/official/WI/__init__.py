import pandas as pd
import us

from ...base import DatasetBaseNoDate
from ..base import ArcGIS

from .counties import WIDane


class Wisconsin(DatasetBaseNoDate, ArcGIS):
    ARCGIS_ID = "ISZ89Z51ft1G16OK"
    source = (
        "https://data.dhsgis.wi.gov/datasets/" "covid-19-historical-data-table/data"
    )
    state_fips = int(us.states.lookup("Wisconsin").fips)
    has_fips = True

    def __init__(self, params=None):
        if params is None:
            params = {
                "f": "json",
                "where": "GEO='State' OR GEO='County'",
                "outFields": "*",
                "returnGeometry": "false",
            }

        super().__init__(params)

    def get(self):

        # Download all data and convert timestamp to date
        crename = {
            "DATE": "dt",
            "GEOID": "fips",
            "NEGATIVE": "negative_tests_total",
            "POSITIVE": "positive_tests_total",
            "DEATHS": "deaths_total",
        }
        df = self.get_all_sheet_to_df(service="COVID19_WI", sheet=10, srvid=1)
        df = df.rename(columns=crename).loc[:, crename.values()]

        # Convert dt
        df["dt"] = df["dt"].map(lambda x: self._esri_ts_to_dt(x))

        # Create total tests
        df["tests_total"] = df.eval("positive_tests_total + negative_tests_total")
        df["cases_total"] = df.eval("positive_tests_total")

        # Reshape data
        out = df.melt(id_vars=["dt", "fips"], var_name="variable_name")
        out = out.dropna(subset=["value"])
        out["fips"] = out["fips"].astype(int)
        out["value"] = out["value"].astype(int)
        out["vintage"] = pd.Timestamp.utcnow().normalize()

        return out
