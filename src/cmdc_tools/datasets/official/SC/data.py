import pandas as pd
import us

from ...base import DatasetBaseNoDate
from ..base import ArcGIS


class SouthCarolina(ArcGIS, DatasetBaseNoDate):
    ARCGIS_ID = "XZg2efAbaieYAXmu"
    has_fips = True
    state_fips = int(us.states.lookup("South Carolina").fips)
    source = "https://services2.arcgis.com/XZg2efAbaieYAXmu/arcgis/rest/services/"

    def get(self):
        overview = self._get_overview()
        hosp = self._get_hosp()

        result = pd.concat([overview, hosp], sort=False).sort_values(["dt", "fips"])
        result.fips = result.fips.astype(int)
        return result

    def _get_overview(self):
        df = self.get_all_sheet_to_df(service="COVID19", sheet=0, srvid=2)

        renamed = df.rename(
            columns={
                "NAME": "county",
                "Areakey": "fips",
                "Confirmed": "cases_confirmed",
                "Recovered": "recovered_total",
                "Death": "deaths_total",
                "Probable_Deaths": "deaths_suspected",
                "Probable_Positives": "cases_suspected",
                # "Total_Neg_Tests": "negative_tests_total",
                # "Total_Pos_Tests": "positive_tests_total",
                "Date_": "dt",
            }
        )

        # Convert dt to datetime
        renamed["dt"] = pd.to_datetime(
            renamed["dt"].map(lambda x: pd.datetime.fromtimestamp(x / 1000).date())
        )
        renamed = (
            renamed.set_index("dt")
            .tz_localize("US/Eastern")
            .tz_convert("UTC")
            .reset_index()
        )
        return (
            renamed[
                [
                    # "county",
                    "fips",
                    "cases_confirmed",
                    "recovered_total",
                    "deaths_total",
                    "deaths_suspected",
                    "cases_suspected",
                    # "negative_tests_total",
                    # "positive_tests_total",
                    "dt",
                ]
            ]
            .melt(id_vars=["dt", "fips"], var_name="variable_name")
            .assign(vintage=pd.Timestamp.utcnow())
        )

    def _get_hosp(self):
        df = self.get_all_sheet_to_df("hospital_beds", 0, 2)

        renamed = df.rename(
            columns={
                "Date": "dt",
                "numbeds": "hospital_beds_capacity_count",
                "numbedsocc": "hospital_beds_in_use_any",
                "numicubeds": "icu_beds_capacity_count",
                "numicubedsocc": "icu_beds_in_use_any",
            }
        )
        renamed["dt"] = pd.to_datetime(
            renamed["dt"].map(lambda x: pd.datetime.fromtimestamp(x / 1000).date())
        )
        renamed = (
            renamed.set_index("dt")
            .tz_localize("US/Eastern")
            .tz_convert("UTC")
            .reset_index()
        )
        return (
            renamed[
                [
                    "dt",
                    "hospital_beds_capacity_count",
                    "hospital_beds_in_use_any",
                    "icu_beds_capacity_count",
                    "icu_beds_in_use_any",
                ]
            ]
            .melt(id_vars=["dt"], var_name="variable_name")
            .assign(vintage=pd.Timestamp.utcnow(), fips=self.state_fips)
        )
