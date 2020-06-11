import pandas as pd

from ...base import DatasetBaseNoDate
from ..base import ArcGIS


class Pennsylvania(ArcGIS, DatasetBaseNoDate):
    ARCGIS_ID = "xtuWQvb2YQnp0z3F"

    def get(self):
        df = self.get_all_sheet_to_df(service="County_Case_Data_Public", sheet=0, srvid=2)

        renamed = df.rename(columns={
            "COUNTY_NAM": "county",
            "Cases": "cases_total",
            "Deaths": "deaths_total",
            "AvailableBedsAdultICU": "available_icu_beds",
            "AvailableBedsMedSurg": "available_other_beds",
            "AvailableBedsPICU": "available_picu_beds",
            "COVID19Hospitalized": "hospital_beds_in_use_covid_confirmed",
            "TotalVents": "ventilators_capacity_count",
            "VentsInUse": "ventilators_in_use_any"
        })

        renamed = renamed[[
            "county",
            "cases_total",
            "deaths_total",
            "available_icu_beds",
            "available_other_beds",
            "available_picu_beds",
            "hospital_beds_in_use_covid_confirmed",
            "ventilators_capacity_count",
            "ventilators_in_use_any"
        ]]
        dt = pd.Timestamp.utcnow().normalize()
        return (
            renamed
            .melt(
                id_vars=['county'],
                var_name="variable_name",
                value_name="value"
            ).assign(dt=dt, vintage=dt)
        )
