import pandas as pd
import re

import us

from ..base import CountyData
from ... import DatasetBaseNoDate

__all__ = ["Alaska"]

county_map = {
    "Anchorage Municipality": 2020,
    "Kenai Peninsula Borough": 2122,
    "Kodiak Island Borough": 2150,
    "Fairbanks North Star Borough": 2090,
    "Southeast Fairbanks Census Area": 2240,
    "Yukon-Koyukuk Census Area": 2290,
    "Matanuska-Susitna Borough": 2170,
    "Nome Census Area": 2180,
    "North Slope Borough": 2185,
    "Northwest Arctic Borough": 2188,
    "Juneau City and Borough": 2110,
    "Ketchikan Gateway Borough": 2130,
    "Petersburg Borough": 2195,
    "Prince of Wales-Hyder Census Area": 2198,
    "Sitka City and Borough": 2220,
    "Bethel Census Area": 2050,
}

DATE_RE = re.compile(r".+last updated on (\d{2}/\d{2}/\d{4}).*")


def _find_col_by_prefix(df, col_prefix):
    cols = [x for x in list(df) if x.lower().startswith(col_prefix.lower())]
    assert len(cols) == 1
    return cols[0]


class Alaska(DatasetBaseNoDate, CountyData):
    table_name = "us_covid"
    pk = '("vintage", "dt", "fips", "variable_id")'
    source = "https://www.arcgis.com/apps/opsdashboard/index.html#/83c63cfec8b24397bdf359f49b11f218"
    state_fips = int(us.states.lookup("Alaska").fips)
    has_fips = True

    def get_cases(self):
        url = "https://www.arcgis.com/sharing/rest/content/items/"
        url += "867f802ce1624b46b40d2bd281490078/data"
        cases_df = pd.read_excel(url, sheet_name="Table 2", skiprows=2)

        bor_col = _find_col_by_prefix(cases_df, "borough")
        comm_col = _find_col_by_prefix(cases_df, "community†")

        # iterate row by row and collect the data we need...
        need_to_find = list(county_map.keys())
        out = []
        finding = None
        for ix in range(cases_df.shape[0]):
            row = cases_df.iloc[ix, :]
            if finding is None and row[bor_col] in need_to_find:
                finding = row[bor_col]
                continue

            if finding is not None and row[comm_col].lower() == "total":
                # this is the row
                out.append(
                    dict(
                        fips=county_map[finding],
                        cases_total=row["All Cases"],
                        hospital_beds_in_use_covid_total=row["Hospitalizations"],
                        deaths_total=row["Deaths"],
                        recovered_total=row["Recovered"],
                        active_total=row["Active"],
                    )
                )
                need_to_find.remove(finding)
                finding = None

        if len(need_to_find) > 0:
            errmsg = f"Could not locate data for {', '.join(need_to_find)}"
            raise ValueError(errmsg)

        # find date
        info = cases_df.iloc[-1, 0].lower().replace("\n", " ")
        date_match = DATE_RE.match(info)
        if date_match is None:
            raise ValueError("Could not find date for this data")

        cases = (
            pd.DataFrame(out)
            .astype(int)
            .melt(id_vars=["fips"])
            .assign(
                dt=pd.to_datetime(date_match[1]),
                vintage=pd.Timestamp.today().normalize(),
            )
        )
        return cases

    def get_tests(self):
        url = "https://opendata.arcgis.com/datasets/"
        url += "af9c1ec2528b468f81b6d7c840a3775c_0.csv"
        df = pd.read_csv(url, parse_dates=["CompletedDate"])
        df["CompletedDate"] = df["CompletedDate"].dt.normalize()
        tot = (
            df.groupby(["CompletedDate", "CountyFIPS"])["Results"]
            .value_counts()
            .rename_axis(index={"Results": "variable"})
            .unstack(level=[1, 2])
            .fillna(0)
            .cumsum()
            .stack(level=0)
            .fillna(0)
            .astype(int)[["Negative", "Positive"]]
            .reset_index()
            .rename(
                columns=dict(
                    Negative="negative_tests_total",
                    Positive="positive_tests_total",
                    CompletedDate="dt",
                    CountyFIPS="fips",
                )
            )
            .melt(id_vars=["dt", "fips"])
            .assign(
                vintage=pd.Timestamp.today().normalize(),
                fips=lambda x: ("2" + x["fips"].astype(str).str.zfill(3)).astype(int),
            )
        )

        return tot

    def get(self):
        cases = self.get_cases()
        tests = self.get_tests()
        out = (
            pd.concat([cases, tests], axis=0, ignore_index=True, sort=True)
            .rename(columns={"variable": "variable_name"})
            .query("fips not in (2300, 2400, 2998, 2999)")
        )
        return out
