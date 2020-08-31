import textwrap

import pandas as pd
import requests
import us

from ...base import DatasetBaseNoDate
from ..base import ArcGIS


class Louisiana(DatasetBaseNoDate, ArcGIS):
    ARCGIS_ID = "O5K6bb5dZVZcTo5M"
    source = "http://ldh.la.gov/Coronavirus/"
    state_fips = int(us.states.lookup("Louisiana").fips)
    has_fips = True

    def _get_county_to_fips(self):
        c2f = self.get_all_sheet_to_df("Counties", 0, 5)

        return c2f.set_index("PARISH")["PFIPS"].to_dict()

    def _get_county_casestests_ts(self):

        column_names = {
            "Lab Collection Date": "dt",
            "Parish": "county",
            "Daily Test Count": "tests_total",
            "Daily Negative Test Count": "negative_tests_total",
            "Daily Positive Test Count": "positive_tests_total",
            "Daily Case Count": "cases_total",
        }
        url = "http://ldh.la.gov/assets/oph/Coronavirus/data/LA_COVID_TESTBYDAY_PARISH_PUBLICUSE.xlsx"
        raw = pd.read_excel(url).rename(columns=column_names)

        return (
            raw.loc[:, list(column_names.values())]
            .set_index(["dt", "county"])
            .unstack()
            .sort_index()
            .cumsum()
            .stack()
            .reset_index()
            .replace({"county": {"DeSoto": "De Soto", "LaSalle": "La Salle"}})
            .assign(fips=lambda x: x["county"].replace(self._get_county_to_fips()))
            .drop(["county"], axis=1)
            .melt(id_vars=["dt", "fips"], var_name="variable_name")
        )

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
            .assign(dt=self._retrieve_dt("US/Central"), variable_name="cases_total",)
            .loc[:, variables]
        )

        # Get deaths
        deaths_cum = (
            cdf.query("Measure == 'Deaths'")
            .groupby("fips")["value"]
            .sum()
            .reset_index()
            .assign(dt=self._retrieve_dt("US/Central"), variable_name="deaths_total",)
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
            .assign(dt=self._retrieve_dt("US/Central"), variable_name="tests_total",)
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
        dt = self._retrieve_dt("US/Central")
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
        qrystr = (
            "ValueType=='death'"
            "& Timeframe != 'cumulative'"
            "& Timeframe != 'current'"
        )
        deaths = (
            ladf.query(qrystr)
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
        ).assign(vintage=self._retrieve_vintage())
        out["fips"] = out["fips"].astype(int)
        out["value"] = out["value"].astype(int)

        return out
