import io
from typing import Optional
import zipfile

import pandas as pd
import requests
import us

from .. import CountyData
from ... import DatasetBaseNeedsDate


class Massachusetts(DatasetBaseNeedsDate, CountyData):
    start_date = "2020-04-29"
    source = (
        "https://www.mass.gov/info-details/"
        "covid-19-response-reporting#covid-19-daily-dashboard-"
    )
    state_fips = int(us.states.lookup("Massachusetts").fips)
    has_fips = False

    def transform_date(self, date: pd.Timestamp) -> pd.Timestamp:
        return date - pd.Timedelta(hours=12)

    def _get_cases_deaths(self, zf: zipfile.ZipFile) -> pd.DataFrame:
        with zf.open("County.csv") as csv_f:
            df = pd.read_csv(csv_f, parse_dates=["Date"])

        column_map = dict(
            Date="dt", Count="cases_total", Deaths="deaths_total", County="county"
        )
        out = df.rename(columns=column_map)
        int_cols = ["cases_total", "deaths_total"]
        out[int_cols] = out[int_cols].fillna(0).astype(int)
        melted = out.melt(id_vars=["dt", "county"], var_name="variable_name")

        return melted.drop_duplicates(
            subset=["dt", "county", "variable_name"], keep="first"
        )

    def _get_hospital_data(
        self, zf: zipfile.ZipFile, date: pd.Timestamp
    ) -> Optional[pd.DataFrame]:
        fn = "HospCensusBedAvailable.xlsx"
        if fn not in [x.filename for x in zf.filelist]:
            print("The file HospCensusBedAvailable.xlsx could not be found, skipping")
            return None
        with zf.open(fn, "r") as f:
            df = pd.read_excel(f, sheet_name="Hospital COVID Census")

        hosp_col = [x for x in list(df) if "including ICU" in x]
        if len(hosp_col) != 1:
            raise ValueError(
                f"Could not find total hospital column from list: {list(df)}"
            )

        icu_col = [x for x in list(df) if "in ICU" in x]
        if len(icu_col) != 1:
            raise ValueError(f"Could not find ICU column from list: {list(df)}")

        column_map = {
            hosp_col[0]: "hospital_beds_in_use_covid_total",
            icu_col[0]: "icu_beds_in_use_covid_total",
        }
        df = df.rename(columns=column_map)
        return (
            df.groupby("Hospital County")[list(column_map.values())]
            .sum()
            .reset_index()
            .rename(columns={"Hospital County": "county"})
            .assign(dt=date)
            .melt(id_vars=["dt", "county"], var_name="variable_name")
        )

    def get(self, date: str) -> pd.DataFrame:
        dt = pd.to_datetime(date)
        ds = dt.strftime("%B-%-d-%Y").lower()
        url = f"https://www.mass.gov/doc/covid-19-raw-data-{ds}/download"
        res = requests.get(url)
        if not res.ok:
            msg = f"Failed request to {url} with code{res.status_code} and message {res.content}"
            raise ValueError(msg)

        buf = io.BytesIO(res.content)
        buf.seek(0)
        dfs = []
        with zipfile.ZipFile(buf) as f:
            dfs.append(self._get_hospital_data(f, dt))
            dfs.append(self._get_cases_deaths(f))

        df = pd.concat([x for x in dfs if x is not None], ignore_index=True)
        df["vintage"] = dt
        return df
