import pandas as pd
import requests
import us

from ...base import DatasetBaseNoDate
from ..base import CountyData


class Connecticut(DatasetBaseNoDate, CountyData):
    has_fips = False
    state_fips = int(us.states.lookup("Connecticut").fips)

    def get(self):
        tests = self._get_tests_data()
        return tests

    def _get_tests_data(self):
        tests_url = (
            "https://data.ct.gov/api/views/qfkt-uahj/rows.csv?accessType=DOWNLOAD"
        )

        df = pd.read_csv(tests_url, parse_dates=True)
        renamed = df.rename(
            columns={
                "Date": "dt",
                "County": "county",
                "Number of tests": "tests_total",
                "Number of positives": "positive_tests_total",
                "Number of negatives": "negative_tests_total",
                # "Number of intedterminates": "unknown_tests_total"
            }
        )

        return renamed[
            [
                "dt",
                "county",
                "tests_total",
                "positive_tests_total",
                "negative_tests_total",
            ]
        ].melt(id_vars=["dt", "county"], var_name="variable_name")
