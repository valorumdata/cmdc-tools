import pandas as pd
import requests
import us

from ...base import DatasetBaseNoDate
from ..base import SODA


class ConnecticutState(DatasetBaseNoDate, SODA):
    baseurl = "https://data.ct.gov"
    has_fips = True
    state_fips = int(us.states.lookup("Connecticut").fips)
    source = "https://data.ct.gov/stories/s/COVID-19-data/wa3g-tfvc/"

    def get(self):
        df_state = self.get_state_data()

        out = pd.concat([df_state], axis=0, ignore_index=True)
        out["vintage"] = pd.Timestamp.now().normalize()

        return out

    def get_state_data(self):
        # Get raw dataframe
        df = self.get_dataset("rf3k-f8fg")

        # Renamers
        crename = {
            "date": "dt",
            "covid_19_pcr_tests_reported": "tests_total",
            "confirmedcases": "positive_tests_total",
            "totaldeaths": "deaths_total",
            "totalcases": "cases_total",
            "hospitalizedcases": "hospital_beds_in_use_covid_total",
        }
        df = df.rename(columns=crename).loc[:, crename.values()]
        df["dt"] = pd.to_datetime(df["dt"])
        df["fips"] = self.state_fips
        for c in [_num for _num in crename.values() if _num != "dt"]:
            df[c] = pd.to_numeric(df.loc[:, c])

        out = df.melt(id_vars=["dt", "fips"], var_name="variable_name")

        return out


class ConnecticutCounty(DatasetBaseNoDate, SODA):
    baseurl = "https://data.ct.gov"
    has_fips = False
    state_fips = int(us.states.lookup("Connecticut").fips)
    source = "https://data.ct.gov/stories/s/COVID-19-data/wa3g-tfvc/"

    def get(self):
        df_county = self.get_county_data()

        out = pd.concat([df_county], axis=0, ignore_index=True)
        out["vintage"] = pd.Timestamp.now().normalize()

        return out

    def get_county_data(self):
        # Get raw dataframe
        cdh_rename = {
            "dateupdated": "dt",
            "county": "county",
            "totalcases": "cases_total",
            "totaldeaths": "deaths_total",
            # "confirmedcases": "positive_tests_total",
            "hospitalization": "hospital_beds_in_use_covid_total",
        }
        cdh = self.get_dataset("bfnu-rgqt").rename(columns=cdh_rename)
        cdh["dt"] = pd.to_datetime(cdh["dt"])
        cdh = cdh.loc[:, cdh_rename.values()]
        for c in [c for c in cdh_rename.values() if (c != "dt") and (c != "county")]:
            cdh[c] = pd.to_numeric(cdh.loc[:, c])

        # Get raw dataframe
        tests_rename = {
            "date": "dt",
            "county": "county",
            "number_of_tests": "tests_total",
            "number_of_positives": "positive_tests_total",
            "number_of_negatives": "negative_tests_total",
        }
        tests = self.get_dataset("qfkt-uahj").rename(columns=tests_rename)
        tests["dt"] = pd.to_datetime(tests["dt"])

        # Turn tests into cumulative
        tests = tests.loc[:, tests_rename.values()]
        for c in [c for c in tests_rename.values() if "tests" in c]:
            tests[c] = pd.to_numeric(tests.loc[:, c])
        tests = tests.loc[~tests["dt"].isna(), :]
        tests = tests.query("county != 'Pending address validation'")

        tests = (
            tests.set_index(["dt", "county"])
            .unstack(level="county")
            .sort_index()
            .cumsum()
            .stack(level="county")
            .reset_index()
        )

        df = cdh.merge(tests, on=["dt", "county"], how="left")

        out = df.melt(id_vars=["dt", "county"], var_name="variable_name")

        return out.dropna()
