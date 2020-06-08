import pandas as pd
import requests

from ...base import DatasetBaseNoDate
from ..base import ArcGIS


class Maryland(ArcGIS, DatasetBaseNoDate):
    ARCGIS_ID = "njFNhDsUCentVYJW"

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
        res = requests.get(self.arcgis_query_url(service="MASTERCaseTracker", sheet=0, srvid=""), params=self.params)
        df = pd.DataFrame.from_records(
            [x['attributes'] for x in res.json()["features"]]
        )
        counties = self.separate_county_specific_data(df)

        keep = df.rename(columns={
            "TotalCases": "cases_total",
            "ReportDate": "dt",
            "NegativeTests": "negative_tests_total",
            "bedsTotal": "hospital_beds_in_use_any",
            "bedsICU": "icu_beds_in_use_any",
            "NegativeTests": "negative_tests_total"
        })
        keep['positive_tests_total'] = keep['TotalTests'] - keep.negative_tests_total

        keep = keep[[
            "cases_total",
            "dt",
            "negative_tests_total",
            "hospital_beds_in_use_any",
            "icu_beds_in_use_any",
            "positive_tests_total"
        ]]
        keep['county'] = "STATE"
        
        # Convert timestamps
        keep["dt"] = keep["dt"].map(
            lambda x: pd.datetime.fromtimestamp(x/1000)
        )
        keep['fips'] = 24
        result = pd.concat([keep, counties], sort=False)

        # Melt
        result = (
            result
            .melt(id_vars=['fips', "dt"], var_name="variable_name")
            .assign(vintage=pd.Timestamp.today().normalize())
        )

        return result.sort_values("dt")


    def separate_county_specific_data(self, df):
        # Gather together all county data
        counties = {
            'ALLE': 1,
            'ANNE': 3,
            'BALT': 5,
            'BCITY': 510,
            'CALV': 9,
            'CARO': 11,
            'CARR': 13,
            'CECI': 15,
            'CHAR': 17,
            'DORC': 19,
            'FRED': 21,
            'GARR': 23,
            'HARF': 25,
            'HOWA': 27,
            'KENT': 29,
            'MONT': 31,
            'PRIN': 33,
            'QUEE': 35,
            'SOME': 39,
            'STMA': 37,
            'TALB': 41,
            'WASH': 43,
            'WICO': 45,
            'WORC': 47,
            'UNKN': 0,
        }

        counties_dfs = []
        for county in counties.keys():
            county_cols = [col for col in df.columns if county in col]
            # Keep the report date column
            county_cols.append("ReportDate")
            county_df = df[county_cols]
            # Rename county columns
            # Need to special case Somerset county
            if county == "SOME":
                county_rename = county_df.rename(columns={
                    f"{county}_": "cases_total",
                    f"death{county}": "deaths_confirmed",
                    "ReportDate": "dt"
                })
            else:
                county_rename = county_df.rename(columns={
                    f"{county}": "cases_total",
                    f"death{county}": "deaths_confirmed",
                    "ReportDate": "dt"
                })
            # Add county name column
            county_rename['county'] = county
            # Remove other columns
            county_rename = county_rename[[
                "cases_total",
                "deaths_confirmed",
                "dt",
                "county"
            ]]
            # Append county df to list
            counties_dfs.append(county_rename)
        # Concat individual county dfs together
        counties_df = pd.concat(counties_dfs)
        # Format timestamps
        counties_df["dt"] = counties_df["dt"].map(
            lambda x: pd.datetime.fromtimestamp(x/1000)
        )

        # Add fips number
        counties_df['fips'] = counties_df.county.map(counties)
        counties_df.fips = counties_df.fips + 21000

        return counties_df
