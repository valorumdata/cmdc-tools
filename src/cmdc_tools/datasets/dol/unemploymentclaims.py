import xml.etree.ElementTree as ET

import pandas as pd
import requests
import us

from ..base import DatasetBaseNoDate, InsertWithTempTable


class StateUIClaims(InsertWithTempTable, DatasetBaseNoDate):
    """
    Interfaces with the Department of Labor's unemployment claims
    data. It does this by downloading the ETA 539 report from:

        https://oui.doleta.gov/unemploy/wkclaims/report.asp

    This data could also be retrieved in a csv format from:

        https://oui.doleta.gov/unemploy/DataDownloads.asp.
    """

    table_name = "dol_ui"
    pk = "(vintage, dt, fips)"

    def __init__(self):
        self.s = requests.Session()
        self.url = "https://oui.doleta.gov/unemploy/wkclaims/report.asp"

        return None

    def _insert_query(self, df: pd.DataFrame, table_name: str, temp_name: str, pk: str):
        _sql_var_insert = f"""
        INSERT INTO data.{table_name} (vintage, dt, fips, variable_name, value)
        SELECT * FROM {temp_name}
        ON CONFLICT (vintage, dt, fips, variable_name) DO NOTHING;
        """

        return _sql_var_insert

    def get(self, states=None):

        if states is None:
            states = [s.abbr for s in us.STATES if not s.is_territory]

        post_dict = [
            ("level", "state"),
            ("final_yr", 2021),
            ("strtdate", 2000),
            ("enddate", 2021),
            ("filetype", "xml"),
        ]
        post_dict.extend([("states[]", s) for s in states])

        # Read in XML file -- I found it easier to work with this than
        # their raw CSV because it at least includes column names...
        xml = self.s.post(self.url, data=post_dict)
        xmltree = ET.fromstring(xml.text)

        # Determine the vintage of the data
        vintage = pd.to_datetime(xmltree.attrib["rundate"])

        # Iterate through items
        rows = []
        for child in list(xmltree):
            values = {}
            for child_child in list(child):
                values[child_child.tag] = child_child.text

            rows.append(values)

        df = pd.DataFrame.from_records(rows)
        df["weekEnded"] = pd.to_datetime(df["weekEnded"])

        # Map state names into fips
        df["vintage"] = vintage
        df["fips"] = df["stateName"].map(
            lambda x: int(us.states.mapping("name", "fips")[x])
        )

        # Rename and drop
        df = df.rename(
            columns={
                "weekEnded": "dt",
                "InitialClaims": "initial_claims",
                "ContinuedClaims": "continued_claims",
                "CoveredEmployment": "covered_employment",
                "InsuredUnemploymentRate": "insured_unemployment_rate",
            }
        )

        outcols = [
            "vintage",
            "fips",
            "dt",
            "initial_claims",
            "continued_claims",
            "covered_employment",
            "insured_unemployment_rate",
        ]
        df = df[outcols].melt(
            id_vars=["vintage", "dt", "fips"],
            var_name="variable_name",
            value_name="value",
        )
        df["value"] = pd.to_numeric(df["value"].str.replace(",", ""))

        return df
