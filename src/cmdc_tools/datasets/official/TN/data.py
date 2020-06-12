import pandas as pd
import requests

from ...base import DatasetBaseNoDate


class Tennessee(DatasetBaseNoDate):

    def get(self):
        daily_cases = self._get_daily_case_info()
        county_data = self._get_county_data()

        df = pd.concat([daily_cases, county_data], sort=False)
        df.county = df.county.fillna("_STATE")
        return (
            df
            .sort_values(['dt', 'county'])
            .fillna(0)
            .melt(
                id_vars=['dt', 'county', 'fips'],
                var_name="variable_name",
                value_name="value"
            )
            .assign(
                vintage=pd.Timestamp.utcnow().normalize()
            )
        )

    def _get_county_data(self):
        url = "https://www.tn.gov/content/dam/tn/health/documents/cedep/novel-coronavirus/datasets/Public-Dataset-County-New.XLSX"
        df = pd.read_excel(url, parse_dates=True)
        cols = {
            "DATE": "dt",
            "COUNTY": "county",
            "TOTAL_CASES": "cases_total", #cummulative
            "TOTAL_CONFIRMED": "cases_confirmed", #cummulative
            "NEW_CONFIRMED": "new_cases_confirmed", #daily
            "POS_TESTS": "positive_tests_total", #cummulative
            "NEG_TESTS": "negative_tests_total", #cummulative
            "TOTAL_DEATHS": "deaths_total", #cummulative
            "NEW_DEATHS": "new_deaths_total", #daily
            "NEW_RECOVERED": "new_recovered_total", #daily
            "TOTAL_RECOVERED": "recovered_total", #cummulative
            "NEW_ACTIVE": "new_active_total", #daily
            "TOTAL_ACTIVE": "active_total", #cummulative
            "NEW_HOSPITALIZED": "hospital_beds_in_use_covid", #daily
            "TOTAL_HOSPITALIZED": "new_hospital_beds_in_use_covid" #daily
        }
        renamed = df.rename(columns=cols)

        return renamed[list(cols.values())]

    def _get_daily_case_info(self):
        url = "https://www.tn.gov/content/dam/tn/health/documents/cedep/novel-coronavirus/datasets/Public-Dataset-Daily-Case-Info.XLSX"
        # res = requests.get(url)
        # return res
        df = pd.read_excel(url, parse_dates=True)
        cols = {
            "DATE": "dt",
            "TOTAL_CASES": "cases_total", #cummulative
            "TOTAL_CONFIRMED": "cases_confirmed", #cummulative
            "NEW_CONFIRMED": "new_cases_confirmed", #daily
            "POS_TESTS": "positive_tests_total", #cummulative
            "NEG_TESTS": "negative_tests_total", #cummulative
            "TOTAL_DEATHS": "deaths_total", #cummulative
            "NEW_DEATHS": "new_deaths_total", #daily
            "NEW_RECOVERED": "new_recovered_total", #daily
            "TOTAL_RECOVERED": "recovered_total", #cummulative
            "NEW_ACTIVE": "new_active_total", #daily
            "TOTAL_ACTIVE": "active_total", #cummulative
            "NEW_HOSP": "hospital_beds_in_use_covid", #daily
            "TOTAL_HOSP": "new_hospital_beds_in_use_covid" #daily
        }
        renamed = df.rename(columns=cols)
        renamed['fips'] = 47
        
        keep_cols = list(cols.values())
        keep_cols.append('fips')
        return renamed[keep_cols]
