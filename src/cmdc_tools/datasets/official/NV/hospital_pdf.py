import camelot
import fitz
import numpy as np
import pandas as pd
import us

from ...base import DatasetBaseNeedsDate
from ..base import CountyData


NVHA_keepcol = [
    (False, "HospitalName"),
    (False, "Region"),
    (False, "Tier"),
    (False, "Zip"),
    (True, "county"),
    (False, "CertNo"),
    (True, "hospital_beds_in_use_any"),
    (True, "hopsital_beds_capacity_count"),
    (False, "hospital_beds_occ_rate"),
    (True, "icu_beds_capacity_count"),
    (True, "icu_beds_in_use_any"),
    (False, "icu_beds_occ_rate"),
    (True, "ventilators_capacity_count"),
    (True, "ventilators_in_use_any"),
    (False, "ventilators_occ_rate"),
    (True, "hospital_beds_in_use_covid_confirmed"),
    (True, "hospital_beds_in_use_covid_suspected"),
    (False, "overflow_covid_total"),
    (False, "overflow_on_vent_covid_total"),
    (False, "hospital_beds_in_use_covid_new"),
    (True, "icu_beds_in_use_covid_total"),
    (True, "icu_beds_in_use_covid_new"),
    (True, "ventilators_in_use_covid_total"),
    (False, "ventilators_used_today"),
    (False, "HFNC_in_use_covid_total"),
    (False, "HFNC_used_today"),
    (False, "patients_develop_covid_symptoms"),
    (False, "covid_patient_deaths_total"),
    (False, "covid_patient_deaths_new"),
    (False, "staff_cases_total"),
    (False, "staffing_levels"),
    (False, "staffing_comments"),
    (False, "N95_supply"),
]


class NVHospitalPdf(DatasetBaseNeedsDate, CountyData):
    state_fips = int(us.states.lookup("Nevada").fips)
    has_fips = False

    def parse_pdf(self, pdf_file):
        # Read the two tables on the page
        tables = camelot.read_pdf(pdf_file)
        hospital_table = pd.concat(
            [tables[0].df.iloc[2:, :-1], tables[1].df], ignore_index=True, axis=0
        )
        hospital_table.columns = [el[1] for el in NVHA_keepcol]

        # For whatever reason, Horizon Specialty Hospital reports
        # 'NEVADA' as their county... Google search reveals that it
        # is in Clark county.
        # A few other counties report 'County' at the end of their
        # county name
        hospital_table["county"] = (
            hospital_table["county"]
            .str.normalize("NFKD")
            .str.title()
            .replace("Nevada", "Clark")
            .str.replace(" County", "")
            .str.strip()
        )
        hospital_table = hospital_table.apply(
            lambda x: pd.to_numeric(x, errors="ignore")
        )

        return hospital_table

    def get(self, pdf_file):
        ht = self.parse_pdf(pdf_file)

        # Only keep columns that we'll use and create new total
        # covid patients
        ht = ht.loc[:, [c for (k, c) in NVHA_keepcol if k]]
        ht["hospital_beds_in_use_covid_total"] = ht.eval(
            "hospital_beds_in_use_covid_confirmed + hospital_beds_in_use_covid_suspected"
        )

        # Reshape and sum variables for entry to database
        ht = ht.groupby("county").sum().reset_index()
        ht = ht.melt(id_vars=["county"], var_name="variable_name")

        ht["vintage"] = pd.Timestamp.utcnow().normalize()
        ht["dt"] = pd.to_datetime(
            fitz.open(pdf_file).getPageText(0).split("\n")[1]
        ).date()

        return ht


if __name__ == "__main__":
    pass
