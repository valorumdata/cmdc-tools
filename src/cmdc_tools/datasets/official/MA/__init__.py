import pandas as pd
import requests
import io
import zipfile
from typing import Optional

from .. import CountyData
from ... import DatasetBaseNeedsDate


class Massachusetts(DatasetBaseNeedsDate, CountyData):
    start_date = "2020-04-29"
    source = (
        "https://www.mass.gov/info-details/"
        "covid-19-response-reporting#covid-19-daily-dashboard-"
    )
    state_fips = 25

    def _insert_query(self, df: pd.DataFrame, table_name: str, temp_name: str, pk: str):
        return f"""
        INSERT INTO data.{table_name} (vintage, dt, fips, variable_id, value)
        SELECT tt.vintage, tt.dt, uf.fips, cv.id, tt.value
        FROM {temp_name} tt
        INNER JOIN (
            SELECT fips, name
            FROM meta.us_fips
            WHERE fips BETWEEN 25000 AND 25999
        ) uf on uf.name = tt.county_name
        LEFT JOIN meta.covid_variables cv on cv.name = tt.variable_name
        ON CONFLICT {pk} DO UPDATE SET value = EXCLUDED.value;
        """

    def _get_cases_deaths(self, zf: zipfile.ZipFile) -> pd.DataFrame:
        with zf.open("County.csv") as csv_f:
            df = pd.read_csv(csv_f, parse_dates=["Date"])

        column_map = dict(
            Date="dt", Count="cases_total", Deaths="deaths_total", County="county_name"
        )
        out = df.rename(columns=column_map)
        int_cols = ["cases_total", "deaths_total"]
        out[int_cols] = out[int_cols].fillna(0).astype(int)
        melted = out.melt(id_vars=["dt", "county_name"], var_name="variable_name")
        return melted.drop_duplicates(
            subset=["dt", "county_name", "variable_name"], keep="first"
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
            .rename(columns={"Hospital County": "county_name"})
            .assign(dt=date)
            .melt(id_vars=["dt", "county_name"], var_name="variable_name")
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
