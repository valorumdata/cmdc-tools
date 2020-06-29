import pandas as pd
import requests
import us

from ...base import DatasetBaseNoDate
from ..base import CountyData


class Connecticut(DatasetBaseNoDate, CountyData):
    has_fips = False
    state_fips = int(us.states.lookup("Connecticut").fips)
    source = (
        "https://data.ct.gov/Health-and-Human-Services/"
        "COVID-19-PCR-Based-Test-Results-by-Date-of-Specime/qfkt-uahj"
    )

    def get(self):
        tests = self._get_tests_data()

        out = pd.concat([tests], axis=0, ignore_index=True)
        out["vintage"] = pd.Timestamp.now().normalize()

        return out

    def _get_tests_data(self):
        tests_url = (
            "https://data.ct.gov/api/views/qfkt-uahj/rows.csv?accessType=DOWNLOAD"
        )

        df = pd.read_csv(tests_url, parse_dates=["Date"])
        df = df.rename(
            columns={
                "Date": "dt",
                "County": "county",
                "Number of tests": "tests_total",
                "Number of positives": "positive_tests_total",
                "Number of negatives": "negative_tests_total",
                # "Number of intedterminates": "unknown_tests_total"
            }
        )

        # Don't currently have tests_total variable in database
        keep = [
            "dt",
            "county",
            "positive_tests_total",
            "negative_tests_total",
            # "tests_total",
        ]
        out = (
            df.loc[:, keep]
            .melt(id_vars=["dt", "county"], var_name="variable_name")
            .dropna()
        )

        return out
