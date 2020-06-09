import pandas as pd
import requests

from ...base import DatasetBaseNoDate
from ..base import ArcGIS


class NewJersey(ArcGIS, DatasetBaseNoDate):
    ARCGIS_ID = "Z0rixLlManVefxqY"

    counties = {
        'ATLANTIC':1,
        'BERGEN':3,
        'BURLINGTON':5,
        'CAMDEN':7,
        'CAPE MAY':9,

        'CUMBERLAND':11,
        'ESSEX':13,
        'GLOUCESTER':15,
        'HUDSON':17,
        'HUNTERDON':19,

        'MERCER':21,
        'MONMOUTH':25,
        'OCEAN':29,
        'PASSAIC':31,
        'SALEM':33,
        'SOMERSET':35,

        'SUSSEX':37,
        'UNION':39,
        'WARREN':41,
        'MORRIS': 27,
        'MIDDLESEX':23,
    }

    def __init__(self, params=None):
        if params is None:
            params = {
                "f": "json",
                "where": "1=1",
                "outFields": "*",
                "returnGeometry": "false",
            }

        super().__init__(params=params)

    
    def get(self):
        cases = self._get_cases()
        hosp = self._get_hospital_data()

        joined = pd.concat([hosp, cases], sort=False)
        
        # Melt
        return (
            joined
            .sort_values(['dt', 'county'])
            .melt(id_vars=["dt", 'county', "fips"], var_name="variable_name")
            .assign(vintage=pd.Timestamp.now().normalize())
        )

    def _get_hospital_data(self):
        url = self.arcgis_query_url(service="PPE_Capacity", sheet=0, srvid=7)
        res = requests.get(url, params=self.params)
        df = pd.DataFrame.from_records(
            [x['attributes'] for x in res.json()["features"]]
        )
        df["survey_period"] = df["survey_period"].map(
            lambda x: pd.datetime.fromtimestamp(x/1000).date()
        )
        df.to_csv("~/Downloads/nj_covid_hosp.csv")
        unstacked = (
            df
            .groupby(['County', 'structure_measure_identifier', "survey_period"])
            .Value
            .max()
            .unstack(level="structure_measure_identifier")
            .fillna(0)
            .astype(int)
        )
        renamed = unstacked.rename(columns={
            "Available Beds - Critical Care": "beds_cc",
            'Available Beds - Intensive Care': "beds_ic",
            'Available Beds - Medical Surgical': "beds_ms",
            'Available Beds - Other': "beds",
            "COVID-19 Positive and PUI Patients Combined in a - Critical Care Bed": "beds_cc_in_use",
            'COVID-19 Positive and PUI Patients Combined in a - Intensive Care Bed': "icu_beds_in_use_covid_total",
            'COVID-19 Positive and PUI Patients Combined in a - Medical Surgical Bed': "beds_ms_in_use",
            'COVID-19 Positive and PUI Patients Combined in a - Other Bed': "beds_in_use",
            'Case count of COVID-19 positive cases currently in the hospital': "total_covid_hosp",
            'Case count of persons under investigation (PUI) / presumptive positive cases currently in the hospital': "cases_suspected",
            'Total # of COVID Patients Currently on a Ventilator': "ventilators_in_use_covid_total",
        })

        renamed = renamed[[
            "beds_cc",
            "beds_ic",
            "beds_ms",
            "beds",
            "beds_cc_in_use",
            "icu_beds_in_use_covid_total",
            "beds_ms_in_use",
            "beds_in_use",
            "total_covid_hosp",
            "cases_suspected",
            "ventilators_in_use_covid_total",
        ]]

        renamed['hospital_beds_in_use_covid_total'] = renamed.beds_cc_in_use + renamed.beds_in_use + renamed.beds_ms_in_use
        renamed['icu_beds_capacity_count'] = renamed.beds_ic + renamed.icu_beds_in_use_covid_total

        renamed = renamed.reset_index()
        renamed = renamed.rename(columns={
            "County": "county",
            "survey_period": "dt"
        })
        renamed.county = renamed.county.str.upper()
        renamed['fips'] = renamed.county.map(self.counties)
        renamed.fips = renamed.fips + 31000
        renamed = renamed[[
            'dt',
            'county',
            'fips',
            "cases_suspected",
            'hospital_beds_in_use_covid_total',
            "icu_beds_in_use_covid_total",
            'icu_beds_capacity_count',
            "ventilators_in_use_covid_total",
        ]]

        return renamed


    def _get_cases(self):
        url = self.arcgis_query_url(service="DailyCaseCounts", sheet=0, srvid=7)
        res = requests.get(url, params=self.params)
        df = pd.DataFrame.from_records(
            [x['attributes'] for x in res.json()["features"]]
        )

        # Rename columns
        keep = df.rename(columns={
            "TOTAL_CASES": "cases_total",
            "TOTAL_DEATHS": "deaths_total",
            "COUNTY": "county"
        })

        # TODO: Add fips
        keep['fips'] = keep.county.map(self.counties)
        keep = keep[["cases_total", "deaths_total", "county", "fips"]]
        dt = pd.Timestamp.now().normalize()
        keep['dt'] = dt
        keep.fips = keep.fips + 34000

        return keep
