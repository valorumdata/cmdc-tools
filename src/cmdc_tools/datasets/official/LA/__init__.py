import pandas as pd
import requests
import textwrap

import us

from ..base import ArcGIS
from ...base import DatasetBaseNoDate


class Louisiana(DatasetBaseNoDate, ArcGIS):
    ARCGIS_ID = "O5K6bb5dZVZcTo5M"
    source = "http://ldh.la.gov/Coronavirus/"
    state_fips = int(us.states.lookup("Louisiana").fips)
    has_fips = True

    def _get_county_to_fips(self):
        c2f = self.get_all_sheet_to_df("Counties", 0, 5)

        return c2f.set_index("PARISH")["PFIPS"].to_dict()

    def _get_county_casestests_ts(self):
        """
        Gets the time series of tests and cases. This data seems to
        often be a few days behind relative to the main data but has
        the benefit of including the history of test/case counts
        """
        # Get the county to fips mapper from the ArcGIS db
        c2f = self._get_county_to_fips()

        # Set rename columns and read data in
        crename = {
            "Lab_Collection_Date": "dt",
            "Parish": "county",
            "Daily_Test_Count": "tests_total",
            "Daily_Case_Count": "cases_total",
        }
        tests = (
            self.get_all_sheet_to_df(
                "Parish_Case_and_Test_Counts_by_Collect_Date", 0, 5
            )
            .rename(columns=crename)
            .loc[:, crename.values()]
        )

        # Create dt
        tests["dt"] = tests["dt"].map(lambda x: self._esri_ts_to_dt(x))

        # Make sure to get cumulative counts
        tests = (
            tests.set_index(["dt", "county"])
            .sort_index()
            .unstack(level="county")
            .cumsum()
            .stack(level="county")
            .reset_index()
            .melt(id_vars=["dt", "county"], var_name="variable_name")
        )
        # For whatever reason they have De Soto/La Salle county as
        # DeSoto/LaSalle -.-
        # Make sure to replace just in case this doesn't get fixed
        tests["county"] = tests["county"].str.replace("DeSoto", "De Soto")
        tests["county"] = tests["county"].str.replace("LaSalle", "La Salle")

        # The conversion to int will fail if one of the counties is
        # missing or misspelled -- This is a feature, not a bug
        tests["fips"] = tests["county"].map(lambda x: c2f.get(x, None)).astype(int)

        return tests.loc[:, ["dt", "fips", "variable_name", "value"]]

    def _get_county_data(self, fulldf):
        # Get the county to fips mapper from the ArcGIS db
        c2f = self._get_county_to_fips()
        variables = ["dt", "fips", "variable_name", "value"]

        # Only keep county data
        cdf = fulldf.query("Group in @c2f.keys()").assign(
            value=lambda x: x["Value"].astype(int),
            fips=lambda x: x["Group"].map(lambda xx: c2f.get(xx, None)).astype(int),
        )

        # Get cases
        cases_cum = (
            cdf.query("Measure == 'Case Count'")
            .groupby("fips")["value"]
            .sum()
            .reset_index()
            .assign(dt=pd.datetime.today().date(), variable_name="cases_total",)
            .loc[:, variables]
        )

        # Get deaths
        deaths_cum = (
            cdf.query("Measure == 'Deaths'")
            .groupby("fips")["value"]
            .sum()
            .reset_index()
            .assign(dt=pd.datetime.today().date(), variable_name="deaths_total",)
            .loc[:, variables]
        )

        # Get cumulative tests -- Both State administered and
        # commercial
        is_test = cdf["Measure"].str.lower().str.contains("test")
        tests_cum = (
            cdf.loc[is_test, :]
            .groupby("fips")["value"]
            .sum()
            .reset_index()
            .assign(dt=pd.datetime.today().date(), variable_name="tests_total",)
            .loc[:, variables]
        )

        out = pd.concat([cases_cum, deaths_cum, tests_cum], ignore_index=True, axis=0)

        return out

    def _get_state_data(self, fulldf):
        """
        Retrieves any of the state level data contained in the
        ArcGIS DataFrame
        """
        # Will create a list of DataFrames
        out = []
        dt = pd.datetime.today().date()
        ladf = fulldf.query("Geography == 'Louisiana'")
        variables = ["dt", "fips", "variable_name", "value"]

        # Total cases -- The timeseries doesn't seem to be kept up to
        # date so not currently using it...
        out.append(
            pd.DataFrame(
                {
                    "dt": dt,
                    "fips": self.state_fips,
                    "variable_name": "cases_total",
                    "value": ladf.query("ValueType == 'case' & Measure == 'age'")
                    .dropna()["Value"]
                    .sum(),
                },
                index=[0],
            )
        )

        # Deaths total -- The timeseries for deaths seems to be kept
        # up to date, so we use it here
        deaths = (
            ladf.query("ValueType=='death' & Timeframe != 'cumulative'")
            .assign(
                dt=lambda x: pd.to_datetime(x["Timeframe"]),
                fips=self.state_fips,
                variable_name="deaths_total",
            )
            .sort_values("dt")
            .query("dt <= @dt")
        )
        deaths["value"] = deaths["Value"].cumsum()
        out.append(deaths.loc[:, variables])

        # Tests -- Everything is just cumulative by parish... Just
        # take a sum
        out.append(
            pd.DataFrame(
                {
                    "dt": dt,
                    "fips": self.state_fips,
                    "variable_name": "tests_total",
                    "value": fulldf.query(
                        "ValueType == 'tests' & Timeframe == 'cumulative'"
                    )["Value"].sum(),
                },
                index=[0],
            )
        )

        # Hospital beds
        hospital_beds = (
            ladf.query("ValueType=='hospitalized' & Timeframe != 'cumulative'")
            .assign(
                dt=lambda x: pd.to_datetime(x["Timeframe"]),
                fips=self.state_fips,
                variable_name="hospital_beds_in_use_covid_total",
            )
            .sort_values("dt")
            .query("dt <= @dt")
        )
        # Forward fill to get the beds in use the prior day for any
        # missing days
        hospital_beds["value"] = hospital_beds["Value"].ffill().astype(int)
        out.append(hospital_beds.loc[:, variables])

        # Ventilators
        vents = (
            ladf.query("ValueType=='on vent' & Timeframe != 'cumulative'")
            .assign(
                dt=lambda x: pd.to_datetime(x["Timeframe"]),
                fips=self.state_fips,
                variable_name="ventilators_in_use_covid_total",
            )
            .sort_values("dt")
            .query("dt <= @dt")
        )
        # Forward fill to get the beds in use the prior day for any
        # missing days
        vents["value"] = vents["Value"].ffill().astype(int)
        out.append(vents.loc[:, variables])

        return pd.concat(out, ignore_index=True, axis=0)

    def get(self):
        # Get the full DF of data from
        fulldf = self.get_all_sheet_to_df("Combined_COVID_Reporting", 0, 5)
        county = self._get_county_data(fulldf)
        county_ct_ts = self._get_county_casestests_ts()
        state = self._get_state_data(fulldf)

        # Concat all of the data together and add vintage
        out = pd.concat(
            [county, county_ct_ts, state], ignore_index=True, axis=0
        ).assign(vintage=pd.Timestamp.utcnow().normalize())

        return out
