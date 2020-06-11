import pandas as pd

from ...base import DatasetBaseNoDate
from ..base import ArcGIS


class Kentucky(ArcGIS, DatasetBaseNoDate):
    ARCGIS_ID = ""

    def arcgis_query_url(self, service, sheet, srvid=1):
        out = f"https://kygisserver.ky.gov/arcgis/rest/services/WGS84WM_Services/{service}/FeatureServer/{sheet}/query"
        return out

    def get(self):
        df = self.get_all_sheet_to_df(
            service="Ky_Cnty_COVID19_Cases_WGS84WM", 
            sheet=0, 
            srvid=""
        )

        renamed = df.rename(columns={
            "County": "county",
            "FIPS": "fips",
            "Hospitalized": "hospital_beds_in_use_covid_confirmed",
            "ICU": "icu_beds_in_use_covid_confirmed",
            "Deceased": "deaths_confirmed",
            "Confirmed": "cases_confirmed"
        })

        renamed = renamed[[
            "county",
            "fips",
            "hospital_beds_in_use_covid_confirmed",
            "icu_beds_in_use_covid_confirmed",
            "deaths_confirmed",
            "cases_confirmed"
        ]]

        return (
            renamed
            .melt(
                id_vars=["county", "fips"],
                var_name="variable_name",
                value_name="value"
            )
            .assign(vintage=pd.Timestamp.utcnow().normalize(), dt=pd.Timestamp.utcnow().normalize())
        )
