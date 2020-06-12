import pandas as pd

from ...base import DatasetBaseNoDate
from ..base import ArcGIS


class Kentucky(ArcGIS, DatasetBaseNoDate):
    ARCGIS_ID = ""

    def arcgis_query_url(self, service, sheet, srvid=1):
        out = f"https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/{service}/FeatureServer/{sheet}/query"
        return out

    def get(self) -> pd.DataFrame:
        df = self.get_all_sheet_to_df(
            service="Ky_Cnty_COVID19_Cases_WGS84WM", sheet=0, srvid=""
        )

        column_map = {
            "County": "county",
            "FIPS": "fips",
            "Hospitalized": "hospital_beds_in_use_covid_confirmed",
            "ICU": "icu_beds_in_use_covid_confirmed",
            "Deceased": "deaths_confirmed",
            "Confirmed": "cases_confirmed",
        }

        renamed = df.rename(columns=column_map).loc[:, list(column_map.values())]

        dt = pd.Timestamp.utcnow().normalize()
        return renamed.melt(
            id_vars=["county", "fips"], var_name="variable_name", value_name="value"
        ).assign(vintage=dt, dt=dt)
