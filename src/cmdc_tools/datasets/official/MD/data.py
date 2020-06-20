import pandas as pd
import requests

from ...base import DatasetBaseNoDate
from ..base import ArcGIS

MD_COUNTY_NF_MAP = {
    "ALLE": 1,
    "ANNE": 3,
    "BALT": 5,
    "BCITY": 510,
    "CALV": 9,
    "CARO": 11,
    "CARR": 13,
    "CECI": 15,
    "CHAR": 17,
    "DORC": 19,
    "FRED": 21,
    "GARR": 23,
    "HARF": 25,
    "HOWA": 27,
    "KENT": 29,
    "MONT": 31,
    "PRIN": 33,
    "QUEE": 35,
    "SOME": 39,
    "STMA": 37,
    "TALB": 41,
    "WASH": 43,
    "WICO": 45,
    "WORC": 47,
}


class Maryland(DatasetBaseNoDate, ArcGIS):
    ARCGIS_ID = "njFNhDsUCentVYJW"
    source = "https://coronavirus.maryland.gov/"
    state_fips = 24
    has_fips = True

    def __init__(self, params=None):

        if params is None:
            params = {
                "f": "json",
                "where": "1=1",
                "outFields": "*",
                "returnGeometry": "false",
            }

        super().__init__(params)

    def get(self):
        # Get main DataFrame
        df = self.get_single_sheet_to_df("MASTERCaseTracker", 0, "", self.params)

        # Split out relevant county data
        cdf = self.separate_county_specific_data(df)

        # Work with State data
        sdf = self.separate_state_specific_data(df)

        # Convert timestamps
        result = pd.concat([cdf, sdf], sort=False)
        result["dt"] = result["dt"].map(
            lambda x: pd.datetime.fromtimestamp(x / 1000).date()
        )
        result["vintage"] = pd.datetime.today().date()

        return result.sort_values("dt").dropna()

    def separate_state_specific_data(self, df):
        """
        This sorts through the DataFrame generated by the master file
        of Maryland COVID data and extracts any of the relevant state
        level data
        """
        # Column renaming conventions
        crenamer = {
            "ReportDate": "dt",
            "bedsTotal": "hospital_beds_in_use_covid_total",
            "bedsICU": "icu_beds_in_use_covid_total",
            "NegativeTests": "negative_tests_total",
            "TotalCases": "cases_total",
            "deaths": "deaths_confirmed",
            "pDeaths": "deaths_suspected",
        }
        # Only have relevant data on these columns
        cols_to_keep = [
            "dt",
            "fips",
            "cases_total",
            "deaths_confirmed",
            "deaths_suspected",
            "deaths_total",
            "hospital_beds_in_use_covid_total",
            "icu_beds_in_use_covid_total",
            "negative_tests_total",
            "positive_tests_total",
        ]

        # Rename and create additional variables
        df = df.rename(columns=crenamer)
        df["positive_tests_total"] = df.eval("(PosTestPercent/100) * TotalTests")
        df["fips"] = self.state_fips

        df = df.loc[:, cols_to_keep]

        df = df.melt(
            id_vars=["dt", "fips"], var_name="variable_name", value_name="value",
        )

        return df

    def separate_county_specific_data(self, df):
        """
        This sorts through the DataFrame generated by the master file
        of Maryland COVID data and extracts any of the relevant county
        level data
        """
        # Only have relevant data on these columns
        cols_to_keep = [
            "dt",
            "fips",
            "cases_total",
            "deaths_confirmed",
            "deaths_suspected",
            "deaths_total",
        ]

        # Gather together all county data
        county_dfs = []
        for (county, cid) in MD_COUNTY_NF_MAP.items():
            # Column renaming conventions
            crenamer = {
                "ReportDate": "dt",
                f"{county}_": "cases_total",  # Somerset is `SOME_`
                f"{county}": "cases_total",  # All others are `{CTY}`
                f"death{county}": "deaths_confirmed",
                f"pDeath{county}": "deaths_suspected",
            }

            # Find out which columns correspond to a particular county
            # but make sure to keep the report date column
            county_cols = [col for col in df.columns if county in col]
            county_cols.append("ReportDate")

            # Only keep the subset of data related to the particular
            # county
            county_df = df[county_cols]

            # Add fips
            county_df["fips"] = self.state_fips * 1000 + cid

            # Rename columns and subset to final data
            county_df = county_df.rename(columns=crenamer)
            county_df["deaths_total"] = county_df.eval(
                "deaths_confirmed + deaths_suspected"
            )
            county_df = county_df.loc[:, cols_to_keep]

            # Append county df to list
            county_dfs.append(county_df)

        # Concat individual county dfs together
        counties_df = pd.concat(county_dfs)

        counties_df = counties_df.melt(
            id_vars=["dt", "fips"], var_name="variable_name", value_name="value",
        )

        return counties_df
