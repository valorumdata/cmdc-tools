import pandas as pd
import us

from ...base import DatasetBaseNoDate
from ..base import ArcGIS


class PuertoRico(DatasetBaseNoDate, ArcGIS):
    ARCGIS_ID = "klquQoHA0q9zjblu"
    state_fips = int(us.states.lookup("Puerto Rico").fips)
    has_fips: bool = True
    source = "https://bioseguridad.maps.arcgis.com/apps/opsdashboard/index.html#/d7308c1abb4747e584329adf1215125e"

    def get(self):

        df = self.get_all_sheet_to_df("Datos_Totales_View7", 0, 5)
        renamed = df.rename(
            columns={
                "T_Camas_Adult_Disp": "adult_hospital_beds_available_any",
                "T_Camas_Adult_Int_Disp": "adult_icu_beds_available_any",
                "T_Paciente_Adult_Int_Covid": "adult_icu_beds_in_use_covid_confirmed",
                "T_Camas_Ped_Int_Disp": "ped_icu_beds_available_any",
                "T_Paciente_Ped_Int_Covid": "ped_icu_beds_in_use_covid_confirmed",
                "T_Vent_Adult_Disp": "adult_ventilators_available",
                "T_Vent_Adult_Covid": "adult_ventilators_in_use_covid_confirmed",
                "T_Vent_Ped_Disp": "ped_ventilators_available",
                "T_Vent_Ped_Covid": "ped_ventilators_in_use_covid_confirmed",
                "T_Casos_Unicos": "cases_confirmed",
                "T_Casos_Neg": "negative_tests_total",
                "T_Hospitalizados": "hospitalized_total",
                "T_Recuperados": "recovered_total",
                "T_Camas_Int_Adult": "adult_icu_beds_capacity_count",
                "T_Camas_Int_Ped": "ped_icu_beds_capacity_count",
                "T_Muertes_Combinadas": "deaths_total",
                "T_Fatalidades": "deaths_confirmed",
                "T_Muertes_COVID_RD": "deaths_suspected",
                "T_Camas_Adulto": "adult_hospital_beds_capacity_count",
                "T_Camas_Ped": "ped_hospital_beds_capacity_count",
                "T_Pacientes_Int_Covid": "icu_beds_in_use_covid_confirmed",
                "T_Vent_Covid": "ventilators_in_use_covid_total",
                "T_Vent_Adult_NoCovid": "adult_ventilators_in_use_any",
                "T_Vent_Ped_NoCovid": "ped_ventilators_in_use_any",
                "Fecha_RD": "dt",
                "T_Casos_Probables_Acumulados": "cases_suspected",
                "T_Paciente_Ped": "ped_hospital_beds_in_use_any",
                "T_Paciente_Adult_NoCovid": "adult_hospital_beds_in_use_any",
                "T_Paciente_Ped_Int_No_Covid": "ped_icu_beds_in_use_any",
                "T_Paciente_Adult_Int_NoCovid": "adult_icu_beds_in_use_any",
            }
        )
        renamed["fips"] = self.state_fips
        return renamed[
            [
                "dt",
                "fips",
                "cases_confirmed",
                "cases_suspected",
                "deaths_total",
                "deaths_confirmed",
                "deaths_suspected",
                "negative_tests_total",
                "hospitalized_total",
                "recovered_total",
                # "icu_beds_in_use_covid_confirmed",
                "ventilators_in_use_covid_total",
                #
                "adult_hospital_beds_capacity_count",
                "adult_hospital_beds_in_use_any",
                #
                "adult_icu_beds_capacity_count",
                "adult_icu_beds_available_any",
                "adult_icu_beds_in_use_covid_confirmed",
                "adult_icu_beds_in_use_any",
                #
                "adult_ventilators_available",
                "adult_ventilators_in_use_any",
                "adult_ventilators_in_use_covid_confirmed",
                #
                "ped_hospital_beds_capacity_count",
                "ped_hospital_beds_in_use_any",
                #
                "ped_icu_beds_capacity_count",
                "ped_icu_beds_in_use_covid_confirmed",
                "ped_icu_beds_in_use_any",
                #
                "ped_ventilators_available",
                "ped_ventilators_in_use_covid_confirmed",
                "ped_ventilators_in_use_any",
            ]
        ].melt(id_vars=["dt", "fips"], var_name="variable_name")
