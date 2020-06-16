import textwrap

import pandas as pd
from .. import InsertWithTempTable, DatasetBaseNeedsDate, DatasetBaseNoDate

BASE_URL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master"


class Locations(InsertWithTempTable, DatasetBaseNoDate):
    table_name = "jhu_locations"
    pk = "uid"

    def __init__(self):
        super().__init__()
        self.url = f"{BASE_URL}/csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv"

    def get(self):
        df = pd.read_csv(self.url)
        df.columns = [x.lower() for x in list(df)]
        df = df.rename(columns=dict(long_="lon"))
        self.df = df
        return df


class JHUDailyReports(InsertWithTempTable, DatasetBaseNeedsDate):
    table_name = "jhu_daily_reports"
    pk = "(date_updated, dt, uid, variable_id)"
    raw_cols = [
        "date_updated",
        "dt",
        "combined_key",
        "cases_total",
        "deaths_total",
        "recovered_total",
        "active_total",
    ]

    def get(self, date):
        # Build URL with date info
        dt = pd.to_datetime(date)
        _date = pd.to_datetime(dt.strftime("%Y-%m-%d"))
        url = f"{BASE_URL}/csse_covid_19_data/csse_covid_19_daily_reports/{dt:%m-%d-%Y}.csv"

        # Read csv file and modify column names
        df = pd.read_csv(url)
        df.columns = [x.lower() for x in list(df)]
        df = df.rename(
            columns={
                "long_": "lon",
                "province/state": "province_state",
                "country/region": "country_region",
                "latitude": "lat",
                "longitude": "lon",
                "confirmed": "cases_total",
                "deaths": "deaths_total",
                "recovered": "recovered_total",
                "active": "active_total",
            }
        )

        # Get date updated information in UTC time
        df["dt"] = _date
        for c in ["last update", "last_update"]:
            if c in df.columns:
                df = df.rename(columns={c: "date_updated"})
                df["date_updated"] = pd.to_datetime(df["date_updated"]).dt.tz_localize(
                    "UTC"
                )
                break
        else:
            df["date_updated"] = None

        # Create the combined location name
        if "combined_key" not in df.columns:
            df["combined_key"] = (
                df["province_state"].fillna("") + ", " + df["country_region"].fillna("")
            )

        # Check for any missing data and fill with 0s
        count_cols = ["cases_total", "deaths_total", "recovered_total", "active_total"]
        if "active_total" not in list(df):
            df["active_total"] = (
                df["cases_total"].fillna(0)
                - df["deaths_total"].fillna(0)
                - df["recovered_total"].fillna(0)
            )
        df[count_cols] = df[count_cols].fillna(0).astype(int)
        self.df = df[self.raw_cols].melt(
            id_vars=["date_updated", "dt", "combined_key"],
            var_name="variable_name",
            value_name="value",
        )

        return self.df

    def _insert_query(self, df, table_name, temp_name, pk):
        out = f"""
        INSERT INTO data.{table_name} (date_updated, dt, uid, variable_id, value)
        SELECT tt.date_updated, tt.dt, l.uid, cv.id as variable_id, tt.value
        from {temp_name} tt
        INNER JOIN data.jhu_locations l ON l.combined_key = tt.combined_key
        INNER JOIN meta.covid_variables cv ON cv.name = tt.variable_name
        ON CONFLICT {pk} DO UPDATE SET value=EXCLUDED.value
        """
        return textwrap.dedent(out)


class JHUDailyReportsUS(JHUDailyReports, DatasetBaseNeedsDate):
    table_name = "jhu_daily_reports_us"
    pk = "(date_updated, dt, fips, variable_id)"
    raw_cols = [
        "fips",
        "dt",
        "date_updated",
        "confirmed",
        "deaths",
        "recovered",
        "active",
        # "incident_rate",
        # "people_tested",
        # "people_hospitalized",
        # "mortality_rate",
        # "testing_rate",
        # "hospitalization_rate",
    ]

    def _insert_query(self, df, table_name, temp_name, pk):
        out = f"""
        INSERT INTO data.{table_name} (date_updated, dt, fips, variable_id, value)
        SELECT tt.date_updated, tt.dt, l.fips, cv.id as variable_id, tt.value
        from {temp_name} tt
        INNER JOIN meta.us_fips l ON l.fips = tt.fips
        INNER JOIN meta.covid_variables cv ON cv.name = tt.variable_name
        ON CONFLICT {pk} DO UPDATE SET value=EXCLUDED.value
        """
        return textwrap.dedent(out)

    def get(self, date):
        # Get date and build url
        dt = pd.to_datetime(date)
        _date = pd.to_datetime(dt.strftime("%Y-%m-%d"))
        url = f"{BASE_URL}/csse_covid_19_data/csse_covid_19_daily_reports_us/{dt:%m-%d-%Y}.csv"

        # Read csv and rename columns
        df = pd.read_csv(url)
        df.columns = [x.lower() for x in list(df)]
        df = df.rename(
            columns={
                "last_update": "date_updated",
                "long_": "lon",
                "confirmed": "cases_total",
                "deaths": "deaths_total",
                "recovered": "recovered_total",
                "active": "active_total",
                # "people_tested": "tests_total"
                # "people_hospitalized": "hospitalized_cumulative"
            }
        )

        # Set date information
        df["date_updated"] = pd.to_datetime(df["date_updated"]).dt.tz_localize("UTC")
        df["dt"] = _date

        # Ignore values without a fips code
        df = df.dropna(subset=["fips"])

        # Store full df but only return subsetted df with melt
        cols_to_keep = [
            "date_updated",
            "dt",
            "fips",
            "cases_total",
            "deaths_total",
            "recovered_total",
            "active_total",
        ]
        self._df_full = df
        self.df = df[cols_to_keep].melt(
            id_vars=["date_updated", "dt", "fips"],
            var_name="variable_name",
            value_name="value",
        )

        return self.df
