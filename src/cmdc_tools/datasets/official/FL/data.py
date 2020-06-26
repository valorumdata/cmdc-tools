import pandas as pd
import us

from ...base import DatasetBaseNoDate
from ..base import ArcGIS


class Florida(DatasetBaseNoDate, ArcGIS):
    ARCGIS_ID = "CY1LXxl9zlJeBuRZ"
    state_fips = int(us.states.lookup("Florida").fips)
    has_fips: bool = True
    source = "https://fdoh.maps.arcgis.com/apps/opsdashboard/index.html#/8d0de33f260d444c852a615dc7837c86"

    def get(self):
        df = self.get_all_sheet_to_df("Florida_COVID19_Cases_by_County_vw", 0, 1)
        renamed = df.rename(
            columns={
                "COUNTY": "fips_prefix",
                "TPositive": "positive_tests_total",
                "TNegative": "negative_tests_total",
                "Deaths": "deaths_total",
                "CasesAll": "cases_total",
                "C_HospYes_Res": "hospital_res",
                "C_HospYes_NonRes": "hosptial_nonres",
            }
        )

        renamed["fips"] = "12" + renamed.fips_prefix
        renamed.fips = renamed.fips.astype(int)
        renamed["dt"] = pd.Timestamp.utcnow().normalize()
        renamed["cumulative_hospitalized"] = (
            renamed.hospital_res + renamed.hosptial_nonres
        )

        return renamed[
            [
                "dt",
                "fips",
                "positive_tests_total",
                "negative_tests_total",
                "deaths_total",
                "cases_total",
                # "cumulative_hospitalized",
            ]
        ].melt(id_vars=["dt", "fips"], var_name="variable_name")
