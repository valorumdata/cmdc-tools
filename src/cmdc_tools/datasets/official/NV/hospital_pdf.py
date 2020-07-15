import camelot
import fitz
import numpy as np
import pandas as pd
import us

from ...base import DatasetBaseNeedsDate
from ..base import CountyData


NVHA_keep_name_added = [
    (False, "HospitalName", pd.to_datetime("2020-03-01")),
    (False, "Region", pd.to_datetime("2020-03-01")),
    (False, "Tier", pd.to_datetime("2020-03-01")),
    (False, "Zip", pd.to_datetime("2020-03-01")),
    (True, "county", pd.to_datetime("2020-03-01")),
    (False, "CertNo", pd.to_datetime("2020-03-01")),
    (True, "hospital_beds_capacity_count", pd.to_datetime("2020-03-01")),
    (True, "hospital_beds_in_use_any", pd.to_datetime("2020-03-01")),
    (False, "hospital_beds_occ_rate", pd.to_datetime("2020-03-01")),
    (True, "icu_beds_capacity_count", pd.to_datetime("2020-03-01")),
    (True, "icu_beds_in_use_any", pd.to_datetime("2020-03-01")),
    (False, "icu_beds_occ_rate", pd.to_datetime("2020-03-01")),
    (True, "ventilators_capacity_count", pd.to_datetime("2020-03-01")),
    (True, "ventilators_in_use_any", pd.to_datetime("2020-03-01")),
    (False, "ventilators_occ_rate", pd.to_datetime("2020-03-01")),
    (True, "hospital_beds_in_use_covid_confirmed", pd.to_datetime("2020-03-01")),
    (True, "hospital_beds_in_use_covid_suspected", pd.to_datetime("2020-03-01")),
    (False, "overflow_covid_total", pd.to_datetime("2020-03-01")),
    (False, "overflow_on_vent_covid_total", pd.to_datetime("2020-03-01")),
    (False, "hospital_beds_in_use_covid_new", pd.to_datetime("2020-03-01")),
    (False, "covid_patients_cleared_but_cannot_discharge", pd.to_datetime("2020-07-08")),
    (True, "icu_beds_in_use_covid_total", pd.to_datetime("2020-03-01")),
    (True, "icu_beds_in_use_covid_new", pd.to_datetime("2020-03-01")),
    (True, "ventilators_in_use_covid_total", pd.to_datetime("2020-03-01")),
    (False, "ventilators_used_today", pd.to_datetime("2020-03-01")),
    (False, "HFNC_in_use_covid_total", pd.to_datetime("2020-03-01")),
    (False, "HFNC_used_today", pd.to_datetime("2020-03-01")),
    (False, "patients_develop_covid_symptoms", pd.to_datetime("2020-03-01")),
    (False, "covid_patient_deaths_total", pd.to_datetime("2020-03-01")),
    (False, "covid_patient_deaths_new", pd.to_datetime("2020-03-01")),
    (False, "staff_cases_total", pd.to_datetime("2020-03-01")),
    (False, "staffing_levels", pd.to_datetime("2020-03-01")),
    (False, "staffing_comments", pd.to_datetime("2020-03-01")),
    (False, "N95_supply", pd.to_datetime("2020-03-01")),
]


class NVHospitalPdf(DatasetBaseNeedsDate, CountyData):
    state_fips = int(us.states.lookup("Nevada").fips)
    has_fips = False

    def determine_cols(self, dt, how="all"):
        if how == "dt":
            keep = lambda x: x[2] <= dt
        elif how == "keep":
            keep = lambda x: x[0]
        else:
            keep = lambda x: x[0] and x[2] <= dt

        return [c[1] for c in NVHA_keep_name_added if keep(c)]

    def get_date(self, pdf_file):
        # Open file and extract text
        f = fitz.open(pdf_file)
        dt = f.getPageText(0).split("\n")[1]

        return pd.to_datetime(dt).date()

    def parse_pdf(self, pdf_file):
        # Get the date
        dt = self.get_date(pdf_file)

        # Get the column names based on whether the column was active
        # on given dt
        cols = self.determine_cols(dt, how="dt")

        # Read all tables on the first page
        tables = camelot.read_pdf(
            pdf_file, pages="1", flavor="lattice", shift_text="",
            layout_kwargs={"char_margin": 0.5}
        )

        rows = []
        for table in tables:
            _df = table.df
            if len(_df.columns) != len(cols):
                msg = "Column counts don't line up\n"
                msg += "Check the columns in the pdf against code cols"
                raise ValueError(msg)

            _df.columns = cols
            for row in _df.itertuples(index=False):
                # Skip any rows with the wrong columns
                if not str(row.Tier).isnumeric():
                    continue
                elif "hospital name" in row.HospitalName.lower():
                    continue
                elif "fail" in row.HospitalName.lower():
                    continue

                # If it makes it this far then add it to the rows
                rows.append(row)
        hospital_table = pd.DataFrame(rows)

        # For whatever reason, Horizon Specialty Hospital reports
        # 'NEVADA' as their county... Google search reveals that it
        # is in Clark county.
        # A few other counties report 'County' at the end of their
        # county name
        # One hospital seems to sometimes report 'Carson' rather than
        # 'Carson City'
        hospital_table["county"] = (
            hospital_table["county"]
            .str.normalize("NFKD")
            .str.title()
            .str.replace(" County", "")
            .replace("Nevada", "Clark")
            .replace("Carson", "Carson City")
            .str.strip()
        )
        hospital_table = hospital_table.apply(
            lambda x: pd.to_numeric(x, errors="ignore")
        )

        return hospital_table

    def get(self, pdf_file):
        # Get date and DataFrame
        dt = self.get_date(pdf_file)
        ht = self.parse_pdf(pdf_file)

        # Only keep columns that we'll use and create new total
        # covid patients
        cols = self.determine_cols(dt, how="all")

        ht = ht.loc[:, cols]
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
