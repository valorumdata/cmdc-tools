import pyppeteer
import us


from ..base import CountyData, ArcGIS
from ...base import DatasetBaseNoDate
from ...puppet import TableauNeedsClick

import pandas as pd


class FloridaHospitalUsage(TableauNeedsClick):

    url = "https://bi.ahca.myflorida.com/t/ABICC/views/Public/HospitalBedsHospital?:isGuestRedirectFromVizportal=y&:embed=y"

    async def _pre_click(self, page: pyppeteer.page.Page):
        await page.waitForSelector(".tabCanvas")

    def _clean_cols(self, df: pd.DataFrame, bads: list, str_cols: list) -> pd.DataFrame:
        for col in list(df):
            for bad in bads:
                df[col] = df[col].astype(str).str.replace(bad, "")
            if col not in str_cols:
                df[col] = pd.to_numeric(df[col])

        return df

    def _clean_df(self, df: pd.DataFrame) -> pd.DataFrame:
        bads = [r",", r"%", "nan"]
        str_cols = ["County", "FileNumber", "ProviderName"]
        df = self._clean_cols(df, bads, str_cols)
        df["county"] = df["County"].str.title()

        # Rename appropriate columns
        df = df.rename(
            columns={
                "Bed Census": "hospital_beds_in_use_any",
                "Total Staffed Bed Capacity": "hospital_beds_capacity_count",
            }
        )

        out_cols = [
            "county",
            "hospital_beds_in_use_any",
            "hospital_beds_capacity_count",
        ]
        return (
            df.query("county != 'Grand Total'")
            .loc[:, out_cols]
            .groupby("county")
            .sum()
            .reset_index()
            .melt(id_vars=["county"], var_name="variable_name")
        )


class FloridaICUUsage(FloridaHospitalUsage):

    url = "https://bi.ahca.myflorida.com/t/ABICC/views/Public/ICUBedsHospital?:isGuestRedirectFromVizportal=y&:embed=y"

    def _clean_df(self, df: pd.DataFrame) -> pd.DataFrame:
        bads = [r",", r"%", "nan"]
        str_cols = ["County", "FileNumber", "ProviderName"]
        df = self._clean_cols(df, bads, str_cols)
        df["county"] = df["County"].str.title()

        df["icu_beds_in_use_any"] = df["Adult ICU Census"] + df["Pediatric ICU Census"]
        df["icu_beds_capacity_count"] = (
            df["Total AdultICU Capacity"] + df["Total PediatricICU Capacity"]
        )
        return (
            df.query("county != 'Grand Total'")
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
    has_fips = False
    state_fips = int(us.states.lookup("Florida").fips)

    def get(self):
        fiu = FloridaICUUsage()
        fhu = FloridaHospitalUsage()
        fhc = FloridaHospitalCovid()
        today = (
            pd.Timestamp.utcnow().tz_convert("US/Eastern").tz_localize(None).normalize()
        )
        vintage = pd.Timestamp.utcnow().normalize()
        return pd.concat(
            [fiu.get(), fhu.get(), fhc.get()], ignore_index=True, sort=True
        ).assign(dt=today, vintage=vintage)


class Florida(DatasetBaseNoDate, ArcGIS):
    ARCGIS_ID = "CY1LXxl9zlJeBuRZ"
    state_fips = int(us.states.lookup("Florida").fips)
    has_fips = True
    source = "https://fdoh.maps.arcgis.com/apps/opsdashboard/index.html#/8d0de33f260d444c852a615dc7837c86"

    def get(self):
        df = self.get_all_sheet_to_df("Florida_COVID19_Cases_by_County_vw", 0, 1)
        df.columns = [x.lower() for x in list(df)]
        column_rename = {
            "county": "fips",
            "t_positive": "positive_tests_total",
            "t_negative": "negative_tests_total",
            "t_total": "tests_total",
            "deaths": "deaths_total",
            "casesall": "cases_total",
        }
        renamed = df.rename(columns=column_rename)
        today = pd.Timestamp.utcnow().normalize()
        renamed["fips"] = renamed["fips"].astype(int) + (self.state_fips * 1000)
        # 12025 is the OLD (retired in 1997) fips code for Date county. It is now known
        # as Miami-Dade county with fips code 12086
        renamed["fips"] = renamed["fips"].replace(12025, 12086)

        return (
            renamed.loc[:, list(column_rename.values())]
            .query("fips not in (12998, 12999)")  # 998: state, 999: unknown
            .melt(id_vars=["fips"], var_name="variable_name")
            .assign(dt=today, vintage=today)
        )
