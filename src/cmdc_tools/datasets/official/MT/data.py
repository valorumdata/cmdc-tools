import pandas as pd
import requests
import textwrap

from ..base import ArcGIS
from ...base import DatasetBaseNoDate


class Montana(ArcGIS, DatasetBaseNoDate):
    def __init__(self, params=None):
        self.ARCGIS_ID = "qnjIrwR8z5Izc0ij"

        if params is None:
            params = {
                "f": "json",
                "where": "1=1",
                "outFields": "*",
                "returnGeometry": "false",
            }

        super().__init__(params)

    def _insert_query(self, df, table_name, temp_name, pk):
        out = f"""
        INSERT INTO data.{table_name} (vintage, dt, fips, variable_id, value)
        SELECT tt.vintage, tt.dt, us.fips, mv.id as variable_id, tt.value
        FROM {temp_name} tt
        LEFT JOIN meta.us_fips us ON tt.county=us.name
        LEFT JOIN meta.covid_variables mv ON tt.variable_name=mv.name
        WHERE us.fips > 30000 AND us.fips < 31000
        ON CONFLICT {pk} DO NOTHING
        """

        return textwrap.dedent(out)

    def get(self):
        dt = pd.Timestamp.today().normalize()

        res = requests.get(
            self.arcgis_query_url(
                service="COVID_Cases_Production_View", sheet=2, srvid=""
            ),
            params=self.params,
        )

        main = pd.DataFrame.from_records(
            [x["attributes"] for x in res.json()["features"]]
        )
        main = main.rename(columns={"County": "county"})

        # get cases
        case_outcome = self.get_cases(main)
        # get hospitalzation
        hbiuc = self.get_hospitalization_stats(main)

        return (
            case_outcome
            # Join tables together
            .join(hbiuc)
            # Reset index
            .reset_index()
            # Melt
            .melt(id_vars=["county"], var_name="variable_name")
            # Normalize
            .assign(vintage=dt, dt=dt)
        )

    def get_cases(self, df):

        case_outcome = (
            df.groupby(["county", "Outcome"])["Sex"]
            .count()
            .unstack(level="Outcome")
            .fillna(0)
            .astype(int)
            .rename(
                columns={
                    "Active": "active_total",
                    "Deceased": "deaths_total",
                    "Recovered": "recovered_total",
                }
            )
        )

        return case_outcome

    def get_hospitalization_stats(self, df):
        hbiuc = (
            df.groupby(["county", "Hospitalization"])["Sex"]
            .count()
            .unstack(level="Hospitalization")
            .fillna(0)
            .astype(int)["Y"]
            .rename("hospital_beds_in_use_covid_total")
        )
        return hbiuc
