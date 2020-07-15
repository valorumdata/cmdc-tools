import io
import urllib.parse

import lxml.html
import pandas as pd
import requests
import us

from ...base import DatasetBaseNeedsDate
from ..base import CountyData


class DC(DatasetBaseNeedsDate, CountyData):
    has_fips = True
    state_fips = int(us.states.lookup("DC").fips)
    source = "https://coronavirus.dc.gov/page/coronavirus-data"
    start_date = pd.to_datetime("2020-04-07")

    def _get_url(self, date: pd.Timestamp):
        # fetch source page and get lxml tree
        res = requests.get(self.source)
        if not res.ok:
            raise ValueError("Could not fetch source of DC page")
        tree = lxml.html.fromstring(res.content)

        # search tree for header of list containing link for date
        xp = "//{el}[contains(text(), '{date:%B %-d, %Y}')]/../following-sibling::ul//a"
        elements = tree.xpath(xp.format(el="strong", date=date))
        if len(elements) == 0:
            elements = tree.xpath(xp.format(el="b", date=date))
        if len(elements) == 0:
            raise ValueError(f"Could not find heading for date {date}")

        # Extract the link text and assert that it has the data we need
        path = elements[0].attrib["href"]
        space_version = urllib.parse.quote(f"{date:%B %-d}")
        assert f"{date:%B-%-d}" in path or space_version in path

        # return the full url of the file, based on whether the path is just the path
        # or if it is the full url
        if path[0] == "/":
            return "https://coronavirus.dc.gov" + path
        elif path.startswith("https"):
            return path
        else:
            raise ValueError(f"Cannot understand path: {path}")

    def get(self, date: str):
        date = pd.to_datetime(date)
        url = self._get_url(date)
        res = requests.get(url)
        if not res.ok:
            raise ValueError(f"Could not fetch DC data for {date}")
        with io.BytesIO(res.content) as fh:
            df = pd.io.excel.read_excel(fh)
        df = df.rename(columns={"Unnamed: 1": "variable_name"}).drop(
            "Unnamed: 0", axis=1
        )

        # Rename and only keep relevant data
        vrename = {
            # Case/Death/Tests
            "Total Positives": "cases_total",
            "Number of Deaths": "deaths_total",
            "Total Overall Tested": "tests_total",
            # ICU
            "Total ICU Beds in Hospitals": "icu_beds_capacity_count",
            "ICU Beds Available": "icu_beds_available",
            "Total COVID-19 Patients in ICU": "icu_beds_in_use_covid_total",
            # Hospitals
            "Total Patients in DC Hospitals (COVID and non-COVID": "hospital_beds_in_use_any",
            "Total Patients in DC Hospitals (COVID and non-COVID)": "hospital_beds_in_use_any",
            "Total COVID-19 Patients in DC Hospitals": "hospital_beds_in_use_covid_total",
            # Ventilators
            "Total Reported Ventilators in Hospitals": "ventilator_capacity_count",
            "In-Use Ventilators in Hospitals": "ventilators_in_use_any",
        }
        df = df.query("variable_name in @vrename.keys()").copy()
        df["variable_name"] = df["variable_name"].replace(vrename)

        # Move date from columns to rows
        df = df.melt(id_vars="variable_name", var_name="dt").dropna()
        df["value"] = df["value"].astype(int)
        df["fips"] = self.state_fips
        df["vintage"] = date.normalize()

        return df
