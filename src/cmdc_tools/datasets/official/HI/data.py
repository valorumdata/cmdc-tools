import pandas as pd
import us

from ...base import DatasetBaseNoDate
from ..base import ArcGIS


class Hawaii(DatasetBaseNoDate, ArcGIS):

    ARCGIS_ID = "HQ0xoN0EzDPBOEci"
    state_fips = int(us.states.lookup("Hawaii").fips)
    has_fips = False
    source = "https://experience.arcgis.com/experience/eb56a98b71324152a918e72d3ccdfc20"

    def get(self):
        df = self.get_all_sheet_to_df("covid_county_counts", 0, "")
        renamed = df.rename(
            columns={
                "cases": "cases_total",
                # "hosp": "hospitalized_total"
                "deaths": "deaths_total",
                "NAME10": "county",
            }
        )
        keep_rows = ["Hawaii", "Honolulu", "Kauai", "Maui"]
        renamed["dt"] = pd.Timestamp.now(tz="US/Hawaii").tz_convert("UTC").normalize()
        renamed = renamed.loc[renamed.county.isin(keep_rows)]
        return (
            renamed[["county", "dt", "cases_total", "deaths_total"]]
            .melt(id_vars=["dt", "county"], var_name="variable_name")
            .assign(vintage=pd.Timestamp.utcnow())
        )
