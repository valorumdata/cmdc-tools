import requests
import pandas as pd

from ... import ArcGIS
from .... import DatasetBaseNoDate


class Imperial(DatasetBaseNoDate, ArcGIS):
    """
    Imperial publishes their county level data in a dashboard that can
    be found at:

    http://www.icphd.org/health-information-and-resources/healthy-facts/covid-19/

    They don't seem to provide any simple interface to their data...
    However, one can directly request data from arcgis itself which is
    the route we take here. They seem to change the service that they
    use to store their data... May need to think about how to deal with
    that

    The base arcgis list can be found at:

    https://services7.arcgis.com/RomaVqqozKczDNgd/ArcGIS/rest/services
    """

    ARCGIS_ID = "RomaVqqozKczDNgd"
    FIPS = 6073
    source = (
        "http://www.icphd.org/health-information-and-resources/healthy-facts/covid-19/"
    )
    state_fips = 6

    def __init__(self):
        self.hospitaloutfields = {
            "DATE": "dt",
            "LICENSED_BEDS": "hospital_beds_capacity_count",
            "HOSPITALIZED_COVID_CONFIRMED_PA": "hospital_beds_in_use_covid_confirmed",
            "HOSPITALIZED_SUSPECTED_COVID_PA": "hospital_beds_in_use_covid_suspected",
            "ICU_BEDS": "icu_beds_capacity_count",
            "ICU_OTHER_PATIENTS": "icu_beds_in_use_other",
            "ICU_SUSPECTED_COVID_PATIENTS": "icu_beds_in_use_covid_suspected",
            "ICU_COVID_CONFIRMED_PATIENTS": "icu_beds_in_use_covid_confirmed",
            "MECHANICAL_VENTILATORS": "ventilators_capacity_count",
            "MECHANICAL_VENTILATORS_IN_USE": "ventilators_in_use_any",
            "MECHANICAL_VENTILATORS_IN_USE_1": "ventilators_in_use_covid_suspected",
            "MECHANICAL_VENTILATORS_IN_USE_F": "ventilators_in_use_covid_confirmed",
        }

        # Default parameter values
        params = {"where": "0=0", "returnGeometry": "false", "f": "pjson"}

        super(Imperial, self).__init__(params=params)

        return None

    def get_hospital_data(self):

        self.params.update({"outFields": ",".join(self.hospitaloutfields)})
        _url = self.arcgis_query_url("EKlhM", 0, 7)
        req = requests.get(_url, params=self.params)

        df = pd.DataFrame.from_records(
            [x["attributes"] for x in req.json()["features"]]
        ).rename(columns=self.hospitaloutfields)
        df["vintage"] = pd.datetime.today()
        df["dt"] = df["dt"].map(lambda x: pd.datetime.fromtimestamp(x / 1000))
        df["fips"] = self.FIPS

        df["icu_beds_in_use_covid_total"] = df.eval(
            "icu_beds_in_use_covid_suspected + icu_beds_in_use_covid_confirmed"
        )
        df["icu_beds_in_use_any"] = df.eval(
            "icu_beds_in_use_covid_total + icu_beds_in_use_other"
        )
        df = df.drop(["icu_beds_in_use_other"], axis="columns")

        df = df.melt(
            id_vars=["vintage", "dt", "fips"],
            var_name="variable_name",
            value_name="value",
        )

        return df

    def get(self):

        # TODO: Eventual also get test data from here
        df = self.get_hospital_data()

        return df
