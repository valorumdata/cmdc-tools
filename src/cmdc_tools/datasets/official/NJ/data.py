import pandas as pd
import requests
import textwrap

from ...base import DatasetBaseNoDate
from ..base import ArcGIS


_NJ_PPA_COLS = {
    "# of new COVID patients (confirmed and PUI) were admitted to the hospital in the past 24 hours": "hospital_beds_in_use_covid_new",
    "COVID-19 Positive and PUI Patients Combined in a - Critical Care Bed": "cc_bed_in_use",
    "COVID-19 Positive and PUI Patients Combined in a - Intensive Care Bed": "icu_bed_in_use",
    "COVID-19 Positive and PUI Patients Combined in a - Medical Surgical Bed": "ms_bed_in_use",
    "COVID-19 Positive and PUI Patients Combined in a - Other Bed": "other_bed_in_use",
    "Case count of COVID-19 positive cases currently in the hospital": "hospital_beds_in_use_covid_confirmed",
    "Case count of persons under investigation (PUI) / presumptive positive cases currently in the hospital": "hospital_beds_in_use_covid_suspected",
    "Total # of COVID Patients Currently on a Ventilator": "ventilators_in_use_covid_total",
}


class NewJersey(DatasetBaseNoDate, ArcGIS):
    """
    Notes:

    * We combine Critical Care and Intensive Care beds under the variable
      `icu_beds_in_use_covid_total`
    """

    ARCGIS_ID = "Z0rixLlManVefxqY"
    source = "https://covid19.nj.gov/#live-updates"

    def __init__(self, params=None):
        super().__init__(params=params)

    def _insert_query(self, df, table_name, temp_name, pk):
        out = f"""
        INSERT INTO data.{table_name} (vintage, dt, fips, variable_id, value)
        SELECT tt.vintage, tt.dt, us.fips, mv.id as variable_id, tt.value
        FROM {temp_name} tt
        LEFT JOIN meta.us_fips us ON tt.county=us.name
        LEFT JOIN meta.covid_variables mv ON tt.variable_name=mv.name
        WHERE us.fips > 34000 AND us.fips < 35000
        ON CONFLICT {pk} DO NOTHING
        """

        return textwrap.dedent(out)

    def get(self):
        cases = self._get_cases()
        hosp = self._get_hospital_data()

        # Concat data
        df = pd.concat([hosp, cases], axis=0).sort_values(["dt", "county"])
        df["vintage"] = pd.Timestamp.now().normalize()

        return df

    def _get_hospital_data(self):
        # Download all data and convert timestamp to date
        df = self.get_all_sheet_to_df(service="PPE_Capacity", sheet=0, srvid=7)
        df["survey_period"] = pd.to_datetime(
            df["survey_period"].map(
                lambda x: pd.datetime.fromtimestamp(x / 1000).date()
            )
        )

        # Group by the county, date, and variable and sum up all values
        df = (
            df.groupby(["County", "structure_measure_identifier", "survey_period"])
            .Value.sum()
            .unstack(level="structure_measure_identifier")
        )

        # Rename and create new variables
        df = df.rename(columns=_NJ_PPA_COLS)
        df["icu_beds_in_use_covid_total"] = df.eval("cc_bed_in_use + icu_bed_in_use")
        df["hospital_beds_in_use_covid_total"] = df.eval(
            "hospital_beds_in_use_covid_suspected + hospital_beds_in_use_covid_confirmed"
        )
        # Another potential way to compute hospital_beds_in_use_covid_total --
        # It usually matches but, when it doesn't, the first way matches the
        # NJ dashboard
        # df["hospital_beds_in_use_covid_total2"] = df.eval(
        #     "cc_bed_in_use + icu_bed_in_use + ms_bed_in_use + other_bed_in_use"
        # )

        # Only keep a subset
        df = df[
            [
                "icu_beds_in_use_covid_total",
                "hospital_beds_in_use_covid_confirmed",
                "hospital_beds_in_use_covid_suspected",
                "hospital_beds_in_use_covid_total",
                "hospital_beds_in_use_covid_new",
                "ventilators_in_use_covid_total",
            ]
        ]
        df = df.reset_index()
        df = df.rename(columns={"County": "county", "survey_period": "dt"})
        df.county = df.county.str.title()
        df.columns.name = ""

        df = df.melt(
            id_vars=["dt", "county"], var_name="variable_name", value_name="value",
        )

        return df

    def _get_cases(self):
        df = self.get_all_sheet_to_df(service="DailyCaseCounts", sheet=0, srvid=7)

        # Rename columns
        df = df.rename(
            columns={
                "TOTAL_CASES": "cases_total",
                "TOTAL_DEATHS": "deaths_total",
                "COUNTY": "county",
            }
        )

        df = df[["county", "cases_total", "deaths_total"]]
        dt = pd.Timestamp.now().normalize()
        df["dt"] = dt

        df = df.melt(
            id_vars=["dt", "county"], var_name="variable_name", value_name="value",
        )

        return df
