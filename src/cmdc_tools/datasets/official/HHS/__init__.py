import pandas as pd

import us

from ..base import ArcGIS, CountyData
from ... import DatasetBaseNoDate


class HHS(DatasetBaseNoDate, ArcGIS):
    """
    This scraper retrieves the hospital data provided by HHS at:

      https://protect-public.hhs.gov/pages/hospital-capacity

    It includes information on hospital capacity, hospital beds in use,
    hospital beds in use by covid patients, icu capacity, icu beds in
    use, and icu beds in use by covid patients
    """

    ARCGIS_ID = "qWZ7BaZXaP5isnfT"
    table_name = "us_covid"
    pk = '("vintage", "dt", "fips", "variable_id")'
    has_fips = True
    state_fips = 0  # Using 0 to denote that this is a national database
    source = "https://protect-public.hhs.gov/pages/hospital-capacity"
    provider = "HHS"

    def _get_percent_reporting(self):
        # TODO: See what pattern for the variable,
        #       `fac_reporting_{}` will look like -- Will they add
        #       new columns or will it always report the date from
        #       yesterday?
        crename = {
            "state_fips": "fips",
            "definitive_fac": "number_of_facilities",
            "fac_reporting_20200720": "number_facilities_reporting",
        }
        # Read percent of facilities reporting data
        df = self.get_all_sheet_to_df(
            "Percentage_of_Facilities_Reporting_by_State", 0, 5
        ).rename(
            columns=crename
        ).loc[:, crename.values()]

        # Convert fips codes to integers
        df["fips"] = df["fips"].astype(int)

        out = df.melt(id_vars=["fips"], var_name="variable_name")

        return out

    def _get_hospital_census(self):
        crename = {
            "state_fips": "fips",
            "total_inpatient_beds": "hospital_beds_capacity_count",
            "total_icu_beds": "icu_beds_capacity_count",
            "icu_beds_used_estimate": "icu_beds_in_use_any",
            "inp_beds_used_estimate": "hospital_beds_in_use_any",
            "inpatient_beds_used_covid_est": "hospital_beds_in_use_covid_total",
            "fac_reporting_20200720": "number_facilities_reporting",
        }
        # Read percent of facilities reporting data
        df = self.get_all_sheet_to_df(
            "NHSN_Percentage_of_Inpatient_Beds_Occupied", 0, 5
        ).rename(
            columns=crename
        ).loc[:, crename.values()]

        # Convert fips codes to integers
        df["fips"] = df["fips"].astype(int)

        out = df.melt(id_vars=["fips"], var_name="variable_name")

        return out

    def get(self):
        df = pd.concat(
            [self._get_percent_reporting(), self._get_hospital_census()],
            axis=0, ignore_index=True
        )

        df["dt"] = (
            pd.Timestamp.utcnow()
                .tz_convert("US/Eastern")
                .tz_localize(None)
                .normalize()
        )
        df["vintage"] = pd.Timestamp.utcnow().normalize()

        # We are storing everything as integers so we need to convert
        # the numbers from estimated floats to integers...
        df["value"] = df["value"].astype(int)
        return df.dropna()
