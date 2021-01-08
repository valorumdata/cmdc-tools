import pandas as pd
import us

from ...base import DatasetBaseNoDate
from ..base import ArcGIS


class Idaho(DatasetBaseNoDate, ArcGIS):
    ARCGIS_ID = "ZOm3lyRvRxR6535t"
    has_fips = False
    state_fips = int(us.states.lookup("Idaho").fips)
    source = "https://services3.arcgis.com/ZOm3lyRvRxR6535t/ArcGIS/rest/services/Dashboard_ID_COVID_CUMULATIVE_BY_COUNTY/FeatureServer"

    def get(self):
        df = self.get_all_sheet_to_df("Dashboard_ID_COVID_CUMULATIVE_BY_COUNTY", 0, 3)
        return df
