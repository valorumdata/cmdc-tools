import numpy as np
import pandas as pd
import us

from ..base import CountyData
from ...base import DatasetBaseNoDate


class MinnesotaCountiesCasesDeaths(DatasetBaseNoDate, CountyData):
    source = "https://mn.gov/covid19/data/covid-dashboard/index.jsp"
    URL = "https://www.health.state.mn.us/diseases/coronavirus/situation.html"
    has_fips = False
    state_fips = int(us.states.lookup("Minnesota").fips)

    def get(self):
        # Download the "maptable" which includes an entry for each
        # county for cases/deaths
        df = pd.concat(pd.read_html(self.URL, attrs={"id": "maptable"}))
        df = df.rename(
            columns={
                "County": "county",
                "Cases": "cases_total",
                "Deaths": "deaths_total",
            }
        )

        # Create datetime
        df["dt"] = pd.Timestamp.utcnow().tz_convert("US/Central").normalize()
        df = df.melt(
            id_vars=["dt", "county"], var_name="variable_name", value_name="value"
        )
        df["vintage"] = pd.Timestamp.utcnow().normalize()

        return df


class Minnesota(DatasetBaseNoDate, CountyData):
    source = "https://mn.gov/covid19/data/covid-dashboard/index.jsp"
    URL = "https://www.health.state.mn.us/diseases/coronavirus/situation.html"
    has_fips = True
    state_fips = int(us.states.lookup("Minnesota").fips)

    def get(self):
        # Get testing data
        # testing = pd.concat(pd.read_html(self.URL, attrs={"id": "labtable"}))
        # testing = testing.rename(
        #     columns={
        #         "Date reported to MDH": "dt",
        #         "Total approximate number of completed tests": "tests_total"
        #     }
        # )

        # Get case data
        cases = pd.concat(pd.read_html(self.URL, attrs={"id": "casetable"}))
        cases = (
            cases.rename(
                columns={
                    "Specimen collection date": "dt",
                    # "Positive cases": "tests_positive_daily",
                    "Cumulative positive cases": "cases_total",
                }
            )
            .loc[:, ["dt", "cases_total"]]
            .query("dt != 'Unknown/missing'")
        )

        # Get death data
        deaths = pd.concat(pd.read_html(self.URL, attrs={"id": "deathtable"}))
        deaths = deaths.rename(
            columns={
                "Date reported": "dt",
                # "Newly reported deaths (daily)": "deaths_new",
                "Total deaths": "deaths_total",
            }
        ).loc[:, ["dt", "deaths_total"]]

        # Get hospital data
        hospkeep = [
            "dt",
            "hospital_bed_in_use_covid_total",
            "icu_bed_in_use_covid_total",
        ]
        hosp = pd.concat(pd.read_html(self.URL, attrs={"id": "hosptable"}))
        hosp = (
            hosp.rename(
                columns={
                    "Date reported": "dt",
                    "Hospitalized, not in ICU (daily)": "hospital_bed_in_use_covid_total",
                    "Hospitalized in ICU (daily)": "icu_bed_in_use_covid_total",
                }
            )
            .loc[:, hospkeep]
            .replace("-", np.nan)
        )

        df = cases.merge(deaths, on="dt", how="outer").merge(hosp, on="dt", how="outer")
        df["dt"] = pd.to_datetime(df["dt"].map(lambda x: x + "/2020"))
        df["fips"] = self.state_fips

        out = (
            df.melt(
                id_vars=["dt", "fips"], var_name="variable_name", value_name="value"
            )
            .dropna()
            .assign(
                vintage=pd.Timestamp.utcnow().normalize(),
                value=lambda x: x["value"].astype(int),
            )
        )
        return out
