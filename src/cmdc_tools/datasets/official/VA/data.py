import pandas as pd

from ...base import DatasetBaseNoDate
from ..base import ArcGIS


class Virginia(ArcGIS, DatasetBaseNoDate):
    ARCGIS_ID = "BkFxaEFNwHqX3tAw"

    def get(self):
        df = self.get_all_sheet_to_df(service="VT_Counties_Cases", sheet=0, srvid=1)

        renamed = df.rename(columns={
            "CntyLabel": "county",
            "CNTYGEOID": "fips",
            "Cases": "cases_total",
            "Deaths": "deaths_total",
            "DateUpd": "dt"
        })
        # Convert Timestamps
        renamed["dt"] = pd.to_datetime(renamed["dt"].map(
            lambda x: pd.datetime.fromtimestamp(x/1000).date()
        ))

        county_summ = self._get_county_summary()


        renamed = renamed[[
            "county",
            "fips",
            "cases_total",
            "deaths_total",
            "dt"
        ]]
        result = pd.concat([renamed, county_summ], sort=False)
        return (
            result
            .sort_values(['dt', 'county'])
            .melt(
                id_vars=['dt', 'county','fips'],
                var_name="variable_name",
                value_name="value"
            )
            .assign(
                vintage=pd.Timestamp.utcnow().normalize()
            )
        )

    def _get_county_summary(self):
        df = self.get_all_sheet_to_df(service="county_summary", sheet=0, srvid=1)

        renamed = df.rename(columns={
            "date": "dt",
            "positive_cases": "positive_tests_total", # daily
            "total_deaths": "cummulative_deaths_total", # cummulative
            "daily_deaths": "deaths_total",
            "daily_recovered": "recovered_total", # daily
            "total_recovered": "cummulative_recovered_total", # cummulative
            "current_hospitalizations": "hospital_beds_in_use_any" # daily
        })

        renamed['negative_tests_total'] = renamed.total_tests - renamed.positive_tests_total

        # Convert Timestamps
        renamed["dt"] = pd.to_datetime(renamed["dt"].map(
            lambda x: pd.datetime.fromtimestamp(x/1000).date()
        ))
        renamed['fips'] = 51


        renamed = renamed[[
            "dt",
            "positive_tests_total",
            "cummulative_deaths_total",
            "deaths_total",
            "recovered_total",
            "cummulative_recovered_total",
            'negative_tests_total',
            "fips"
        ]]

        return renamed
