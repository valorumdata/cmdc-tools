#%% setup
import textwrap
import requests
import pandas as pd
from cmdc.datasets import OnConflictNothingBase



class CANTimeseries(OnConflictNothingBase):
    URL = "https://data.covidactnow.org/latest/us/{geo}.{intervention}_INTERVENTION.timeseries.json"
    pk = '("date", "vintage", "intervention_id", "fips")'
    table_name = "actnow_county_timeseries"

    def __init__(self, intervention="OBSERVED"):
        super().__init__()
        self.intervention = intervention

    @property
    def url(self):
        return self.URL.format(intervention=self.intervention, geo=self.geo)

    def _unpack(self, js):
        colmap = dict(
            date="date",
            lastUpdatedDate="vintage",
            intervention="intervention",
            fips="fips",
            hospitalBedsRequired="hospital_beds_required",
            hospitalBedCapacity="hospital_bed_capacity",
            ICUBedsInUse="icu_beds_in_use",
            ICUBedCapacity="icu_bed_capacity",
            ventilatorsInUse="ventilators_in_use",
            ventilatorCapacity="ventilator_capacity",
            RtIndicator="rt_indicator",
            RtIndicatorCI90="rt_indicator_ci_90",
            cumulativeDeaths="cumulative_deaths",
            cumulativeInfected="cumulative_infected",
            cumulativePositiveTests="cumulative_positive_tests",
            cumulativeNegativeTests="cumulative_negative_tests",
        )
        dfs = []
        for county in js:
            new_df = (
                pd.DataFrame(county["timeseries"])
                .assign(
                    fips=county["fips"],
                    lastUpdatedDate=county["lastUpdatedDate"],
                    intervention=self.intervention + "_INTERVENTION"
                )
                .rename(columns=colmap)
            )
            dfs.append(new_df)
        df = pd.concat(dfs, ignore_index=True)
        return df

    def get(self):
        res = requests.get(self.url)
        if not res.ok:
            raise ValueError("Could not fetch data from url: {}".format(url))

        js = res.json()
        df = self._unpack(js)
        for c in ["date", "vintage"]:
            df[c] = pd.to_datetime(df[c])

        df["fips"] = df["fips"].astype(int)

        return df

    def _insert_query(self, df, table_name, temp_name, pk):
        cols = list(df)
        intervention_ix = cols.index("intervention")
        final_cols = cols.copy()
        final_cols[intervention_ix] = "intervention_id"

        temp_cols = list(df)
        temp_cols[intervention_ix] = "it.id as intervention_id"

        out = f"""
        INSERT INTO data.{table_name} ({", ".join(final_cols)})
        SELECT {", ".join(temp_cols)}
        from {temp_name} tt
        LEFT JOIN meta.actnow_intervention_types it on it.name = tt.intervention
        ON CONFLICT {pk} DO NOTHING
        """
        return textwrap.dedent(out)


class CANCountyTimeseries(CANTimeseries):
    geo = "counties"

class CANStateTimeseries(CANTimeseries):
    table_name = "actnow_state_timeseries"
    geo = "states"


class CANActuals(CANTimeseries):
    pk = '("vintage", "date", "fips")'
    def _unpack(self, js):
        colmap = dict(
            lastUpdatedDate="vintage",
            population="population",
            intervention="intervention",
            cumulativeConfirmedCases="cumulative_confirmed_cases",
            cumulativePositiveTests="cumulative_positive_tests",
            cumulativeNegativeTests="cumulative_negative_tests",
            cumulativeDeaths="cumulative_deaths",
            contactTracers="contact_tracers",
            date="date",
            hospital_beds_capacity="hospital_beds_capacity",
            hospital_beds_totalCapacity="hospital_beds_total_capacity",
            hospital_beds_currentUsageCovid="hospital_beds_current_usage_covid",
            hospital_beds_currentUsageTotal="hospital_beds_current_usage_total",
            hospital_beds_typicalUsageRate="hospital_beds_typical_usage_rate",
            icu_beds_capacity="icu_beds_capacity",
            icu_beds_totalCapacity="icu_beds_total_capacity",
            icu_beds_currentUsageCovid="icu_beds_current_usage_covid",
            icu_beds_currentUsageTotal="icu_beds_current_usage_total",
            icu_beds_typicalUsageRate="icu_beds_typical_usage_rate",
        )
        dfs = []
        for county in js:
            base = (
                pd.DataFrame(county["actualsTimeseries"])
                .assign(
                    fips=county["fips"],
                    lastUpdatedDate=county["lastUpdatedDate"],
                )
                .drop(["population", "contactTracers"], axis=1)
            )

            hbeds = base.pop("hospitalBeds")
            hdf = pd.DataFrame(list(hbeds))
            hdf.columns = [f"hospital_beds_{n}" for n in list(hdf)]

            ibeds = base.pop("ICUBeds")
            idf = pd.DataFrame(list(ibeds))
            idf.columns = [f"icu_beds_{n}" for n in list(idf)]

            new_df = pd.concat([base, hdf, idf], axis=1).rename(columns=colmap)
            for c in ["date", "vintage"]:
                new_df[c] = pd.to_datetime(new_df[c])

            for c in set(list(new_df)) - set(["date", "vintage", "intervention"]):
                new_df[c] = pd.to_numeric(new_df[c])

            dfs.append(new_df)

        return pd.concat(dfs, ignore_index=True)


class CANCountyActuals(CANActuals):
    table_name = "actnow_county_actuals"
    geo = "counties"

class CANStateActuals(CANActuals):
    table_name = "actnow_state_actuals"
    geo = "states"

# %%
