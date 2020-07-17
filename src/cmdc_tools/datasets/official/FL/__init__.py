import pyppeteer
import us
from cmdc_tools.datasets import DatasetBaseNoDate

from ..base import CountyData
from ...puppet import TableauNeedsClick

import pandas as pd


class FloridaHospitalUsage(TableauNeedsClick):

    url = "https://bi.ahca.myflorida.com/t/ABICC/views/Public/ICUBedsHospital?:isGuestRedirectFromVizportal=y&:embed=y"

    async def _pre_click(self, page: pyppeteer.page.Page):
        await page.waitForSelector(".tabCanvas")

    def _clean_df(self, df: pd.DataFrame) -> pd.DataFrame:
        str_cols = ["County", "FileNumber", "ProviderName"]
        for col in list(df):
            for bad in (r",", r"%", "nan"):
                df[col] = df[col].astype(str).str.replace(bad, "")
            if col not in str_cols:
                df[col] = pd.to_numeric(df[col])

        df["icu_beds_in_use_any"] = df["Adult ICU Census"] + df["Pediatric ICU Census"]
        df["icu_beds_capacity_count"] = (
            df["Total AdultICU Capacity"] + df["Total PediatricICU Capacity"]
        )
        return (
            df.rename(columns={"County": "county"})
            .query("county != 'Grand Total'")
            .loc[:, ["county", "icu_beds_capacity_count", "icu_beds_in_use_any"]]
            .groupby("county")
            .sum()
            .reset_index()
            .melt(id_vars=["county"], var_name="variable_name")
        )


class FloridaHospitalCovid(TableauNeedsClick):
    url = "https://bi.ahca.myflorida.com/t/ABICC/views/Public/COVIDHospitalizationsCounty?:isGuestRedirectFromVizportal=y&:embed=y"

    def _clean_df(self, df: pd.DataFrame) -> pd.DataFrame:
        column_name = "hospital_beds_in_use_covid_total"
        df.columns = ["county", column_name]
        df = df.query("county != 'Grand Total'")
        df.loc[:, column_name] = (
            df.loc[:, column_name].astype(str).str.replace(",", "").astype(int)
        )
        return df.melt(id_vars=["county"], var_name="variable_name")


class FloridaHospital(DatasetBaseNoDate, CountyData):
    source = FloridaHospitalUsage.url
    provider = "county"
    has_fips = False
    state_fips = int(us.states.lookup("Florida").fips)

    def get(self):
        fhu = FloridaHospitalUsage()
        fhc = FloridaHospitalCovid()
        today = pd.Timestamp.utcnow().normalize()
        return pd.concat([fhu.get(), fhc.get()], ignore_index=True, sort=True).assign(
            dt=today, vintage=today
        )
