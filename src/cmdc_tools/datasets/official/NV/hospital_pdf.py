import camelot
import fitz
import numpy as np
import pandas as pd
import us

from ...base import DatasetBaseNeedsDate
from ..base import CountyData


_COLS = [
    (0, "name"),
    (4, "county"),
    # 8 corresponds to staffed beds -- Should we use licensed beds
    # instead?
    (8, "hospital_beds_capacity_count"),
    (11, "hospital_beds_in_use_any"),
    (14, "icu_beds_capacity_count"),
    (16, "icu_beds_in_use_any"),
    (22, "ventilators_capacity_count"),
    (24, "ventilators_in_use_any"),
    (26, "hospital_beds_in_use_covid_confirmed"),
    (29, "hospital_beds_in_use_covid_suspected"),
    (34, "hospital_beds_in_use_covid_new"),
    (36, "icu_beds_in_use_covid_total"),
    (39, "ventilators_in_use_covid_total"),
]


class NVHospitalPdf(DatasetBaseNeedsDate, CountyData):
    state_fips = int(us.states.lookup("Nevada").fips)
    has_fips = False
    source = "https://nvha.net/"

    def get_date(self, pdf_file):
        # Open file and extract text
        f = fitz.open(pdf_file)

        # Be defensive because they sometimes put "CORRECTED" as
        # first line -- Should usually happen as element 1 or 2
        # but check the first 5 lines just in case
        ptxt = f.getPageText(0).split("\n")
        for line in ptxt[:5]:
            dt = pd.to_datetime(line, errors="ignore")
            if type(dt) is not str:
                break

        return dt.date()

    def parse_pdf(self, pdf_file):
        # Get the date
        dt = self.get_date(pdf_file)

        # Read all tables on the first page
        tables = camelot.read_pdf(
            pdf_file, pages="1,2,7,8", flavor="lattice",
            shift_text="", strip_text="\n",
            layout_kwargs={"char_margin": 0.5}
        )
        # Organize tables by which type they are
        t1_tables = [0, 2, 3]
        t2_tables = [1, 4, 5]
        tables_w_headers = [0, 1, 2, 4]

        # Pull out correct column labels
        t1_headers = tables[0].df.iloc[0, :]
        t1_headers[0] = "name"
        t2_headers = tables[1].df.iloc[0, :]
        t2_headers[0] = "name"
        agg_regions = ['total', 'south', 'rural', 'north']

        dfs = []
        for (itable, table) in enumerate(tables):
            # Get correct subset of data
            if itable in tables_w_headers:
                _df = table.df.iloc[1:, :]
            else:
                _df = table.df

            if itable in t1_tables:
                _df.columns = t1_headers
            elif itable in t2_tables:
                _df.columns = t2_headers
            else:
                raise ValueError("Unexpected table")

            _df["name"] = _df["name"].str.lower()
            _df = _df.query(
                "(name not in @agg_regions) & (name != '')"
            )
            dfs.append(_df)

        # Stack matching dfs and then merge
        t1_df = pd.concat(
            [dfs[i] for i in t1_tables], axis=0, ignore_index=True
        )
        t2_df = pd.concat(
            [dfs[i] for i in t2_tables], axis=0, ignore_index=True
        )
        hospital_table = t1_df.merge(t2_df, on="name", how="outer")

        # Rename columns that we're interested in
        hospital_table = hospital_table.iloc[:, [c[0] for c in _COLS]]
        hospital_table.columns = [c[1] for c in _COLS]

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

        ht["hospital_beds_in_use_covid_total"] = ht.eval(
            "hospital_beds_in_use_covid_confirmed + hospital_beds_in_use_covid_suspected"
        )

        # Reshape and sum variables for entry to database
        ht = ht.groupby("county").sum().reset_index()
        ht = ht.melt(id_vars=["county"], var_name="variable_name")

        ht["vintage"] = self._retrieve_vintage()
        ht["dt"] = dt

        ht = ht.dropna()
        ht["value"] = ht["value"].astype(int)

        return ht
