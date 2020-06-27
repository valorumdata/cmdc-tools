import pandas as pd

from .. import InsertWithTempTable, DatasetBaseNoDate


class KeystonePolicy(InsertWithTempTable, DatasetBaseNoDate):
    """
    Retrieves the Keystone data and reshapes it in a particular way
    such that each row of the DataFrame is indexed by a date, fips
    code, and an NPI policy.

    Note that the reference url is the "inherited policies" which
    enforces that the county restrictions are no less strict than what
    is being imposed at the state level -- If there was no gather
    restriction issued by the county but the state had a gathering
    restriction then we assume that the county is under the state's
    restriction
    """

    table_name = "npi_interventions"
    pk = "(vintage, dt, location, variable_id)"
    data_type = "general"
    source = "https://github.com/Keystone-Strategy/covid19-intervention-data"
    url = (
        "https://raw.githubusercontent.com/Keystone-Strategy/"
        "covid19-intervention-data/master/complete_npis_inherited_policies.csv"
    )

    def _insert_query(self, df: pd.DataFrame, table_name: str, temp_name: str, pk: str):

        out = f"""
        INSERT INTO data.{table_name} (vintage, dt, location, variable_id, value)
        SELECT tt.vintage, tt.dt, tt.fips as location, nv.id, tt.value
        FROM {temp_name} tt
        LEFT JOIN meta.npi_variables nv ON nv.name=tt.variable_name
        ON CONFLICT {pk} DO UPDATE SET value=EXCLUDED.value;
        """

        return out

    def _reshape_npi(self, df, columns, dates):
        # Only use columns requested
        sub_df = df.query("npi in @columns")

        # For each date, create a DataFrame that determines whether
        # each fips/npi combination was active during that date
        dfs = pd.concat(
            [
                pd.DataFrame(
                    {
                        "dt": _date,
                        "fips": sub_df["fips"],
                        "variable_name": sub_df["npi"],
                        "value": sub_df.eval(
                            "(start_date <= @_date) & (end_date > @_date)"
                        ),
                    }
                )
                for _date in dates
            ],
            axis=0,
            ignore_index=True,
        )

        # We need to groupby dt/fips/npi in case there were multiple
        # instances of the npi being started
        out = dfs.groupby(["dt", "fips", "variable_name"]).any().reset_index()

        return out

    def get(self):
        """
        Fetches the NPI data

        Returns
        -------
        df : pd.DataFrame
            A DataFrame with a separate entry for each location, each
            NPI, and each day between March 1, 2020 and current with a
            boolean that indicates whether the NPI was active in that
            location on that day
        """
        # Get dates between March 1, 2020 and today
        dates = pd.date_range("2020-03-01", pd.datetime.now(), freq="D")

        # Fetch data
        df = pd.read_csv(
            self.url,
            usecols=["fips", "npi", "start_date", "end_date"],
            parse_dates=["start_date", "end_date"],
        )
        # Rename for consistency's sake
        df = df.rename(columns={"school closure": "school_closure"})

        # We must work with "gathering" size limits separately due to
        # the fact that there are stages of gathering limits, but for
        # others, we can simply determine whether
        simple_npis = [
            "closing_of_public_venues",
            "lockdown",
            "school_closure",
            "non-essential_services_closure",
            "shelter_in_place",
            "social_distancing",
            "religious_gatherings_banned",
        ]
        outs = self._reshape_npi(df, simple_npis, dates)

        # We now work with the gathering columns
        gathering_cols = [
            "gathering_size_10_0",
            "gathering_size_25_11",
            "gathering_size_100_26",
            "gathering_size_500_101",
        ]
        # First grab and determine whether any of the gathering
        # restrictions were imposed at a particular date
        _outg = self._reshape_npi(df, gathering_cols, dates)

        # Reshape this so that the different categories are along the
        # columns
        outg_pivot = _outg.pivot_table(
            index=["dt", "fips"], columns="variable_name", values="value"
        ).loc[:, gathering_cols]

        # Finally, we set value to True if any of the more strict
        # gathering restrictions were in place
        outg = (
            (outg_pivot.cumsum(axis=1) > 0)
            .reset_index()
            .melt(id_vars=["dt", "fips"], var_name="variable_name", value_name="value")
        )

        out = pd.concat([outs, outg], axis=0, ignore_index=True)
        out["vintage"] = pd.Timestamp.utcnow().normalize()

        return out
