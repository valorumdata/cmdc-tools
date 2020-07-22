import textwrap
import pandas as pd
import us

from ...base import DatasetBaseNoDate
from ..base import ArcGIS


class Pennsylvania(DatasetBaseNoDate, ArcGIS):
    ARCGIS_ID = "xtuWQvb2YQnp0z3F"
    source = (
        "https://www.arcgis.com/apps/opsdashboard/"
        "index.html#/85054b06472e4208b02285b8557f24cf"
    )
    state_fips = int(us.states.lookup("Pennsylvania").fips)
    has_fips = False

    def get(self):
        df = self.get_all_sheet_to_df(
            service="County_Case_Data_Public", sheet=0, srvid=2
        )

        column_map = {
            "COUNTY_NAM": "county",
            "Cases": "cases_total",
            "Deaths": "deaths_total",
            "AvailableBedsAdultICU": "available_icu_beds",
            "COVID19Hospitalized": "hospital_beds_in_use_covid_total",
            "TotalVents": "ventilators_capacity_count",
            "VentsInUse": "ventilators_in_use_any",
            "COVID19onVents": "ventilators_in_use_covid_total",
        }

        renamed = df.rename(columns=column_map)

        # the column we used was non-covid, need to add covid to get total
        renamed["ventilators_in_use_any"] += renamed["ventilators_in_use_covid_total"]
        renamed = renamed.loc[:, list(column_map.values())]

        return renamed.melt(
            id_vars=["county"], var_name="variable_name", value_name="value"
        ).dropna().assign(
            dt=self._retrieve_dt("US/Eastern"),
            vintage=self._retrieve_vintage(),
            value=lambda x: x["value"].astype(int)
        )
