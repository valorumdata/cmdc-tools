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

    def _insert_query(self, df: pd.DataFrame, table_name: str, temp_name: str, pk: str):
        out = f"""
        INSERT INTO data.{table_name} (vintage, dt, fips, variable_id, value)
        SELECT tt.vintage, tt.dt, mc.fips, mv.id as variable_id, tt.value
        FROM {temp_name} tt
        INNER JOIN meta.covid_variables mv ON tt.variable_name=mv.name
        LEFT JOIN (
            SELECT fips, name
            FROM meta.us_fips WHERE state = LPAD({self.state_fips}::TEXT, 2, '0')
        ) mc on LOWER(mc.name) = LOWER(tt.county)
        ON CONFLICT {pk} DO NOTHING
        """

        return textwrap.dedent(out)

    def get(self):
        df = self.get_all_sheet_to_df(
            service="County_Case_Data_Public", sheet=0, srvid=2
        )

        column_map = {
            "COUNTY_NAM": "county",
            "Cases": "cases_total",
            "Deaths": "deaths_total",
            "AvailableBedsAdultICU": "available_icu_beds",
            "AvailableBedsMedSurg": "available_other_beds",
            "AvailableBedsPICU": "available_picu_beds",
            "COVID19Hospitalized": "hospital_beds_in_use_covid_confirmed",
            "TotalVents": "ventilators_capacity_count",
            "VentsInUse": "ventilators_in_use_any",
            "COVID19onVents": "ventilators_in_use_covid_confirmed",
        }

        renamed = df.rename(columns=column_map)

        # the column we used was non-covid, need to add covid to get total
        renamed["ventilators_in_use_any"] += renamed[
            "ventilators_in_use_covid_confirmed"
        ]

        renamed = renamed.loc[:, list(column_map.values())]
        dt = pd.Timestamp.utcnow().normalize()
        return renamed.melt(
            id_vars=["county"], var_name="variable_name", value_name="value"
        ).assign(dt=dt, vintage=dt)
