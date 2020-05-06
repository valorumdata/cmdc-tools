import pandas as pd
from cmdc.datasets import OnConflictNothingBase

BASE_URL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master"


class Locations(OnConflictNothingBase):
    table_name = "jhu_locations"
    pk = "uid"

    def __init__(self):
        self.url = f"{BASE_URL}/csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv"
        pass

    def get(self):
        df = pd.read_csv(self.url)
        df.columns = [x.lower() for x in list(df)]
        df = df.rename(columns=dict(long_="lon"))
        self.df = df
        return df


class DailyReports(OnConflictNothingBase):
    table_name = "jhu_daily_reports"
    pk = "(combined_key, date_updated)"

    def get(self, date):
        dt = pd.to_datetime(date)
        url = f"{BASE_URL}/csse_covid_19_data/csse_covid_19_daily_reports/{dt:%m-%d-%Y}.csv"
        df = pd.read_csv(url)
        df.columns = [x.lower() for x in list(df)]
        df = df.rename(columns={
            "long_": "lon",
            "province/state": "province_state",
            "country/region": "country_region",
            "latitude": "lat",
            "longitude": "lon",
        })
        for c in ["last update", "last_update"]:
            if c in df.columns:
                df = df.rename(columns={c: "date_updated"})
                df["date_updated"] = (
                    pd.to_datetime(df["date_updated"]).dt.tz_localize("UTC")
                )
                break
        else:
            df["date_updated"] = None

        if "combined_key" not in df.columns:
            df["combined_key"] = (
                df["province_state"].fillna("") + ", " +
                df["country_region"].fillna("")
            )


        self.df = df
        return df
