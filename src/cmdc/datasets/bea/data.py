#%% setup
from concurrent.futures import ThreadPoolExecutor
import textwrap
import os
import requests
import pandas as pd

from cmdc.datasets.base import OnConflictNothingBase

KEY = os.environ.get("BEA_KEY", None)


def _make_bea_request(key=KEY, **kw):
    if key is None:
        raise ValueError(
            "Must provide `key` argument or set BEA_KEY environment variable"
        )
    base = f"https://apps.bea.gov/api/data"

    args = dict(UserID=key)
    args.update(kw)
    res = requests.get(base, params=args)
    if not res.ok:
        msg = f"Unsuccessful request: {res.text}"
        raise ValueError(msg)

    return res.json()["BEAAPI"]


def _build_variable_dataframe():
    res = _make_bea_request(
        Method="GetParameterValuesFiltered",
        DatasetName="Regional",
        TargetParameter="LineCode",
        TableName="CAGDP2",
    )
    prefix = "[CAGDP2] Gross Domestic Product (GDP): "
    df = (
        pd.DataFrame(res["Results"]["ParamValue"])
        .rename(columns={"Key": "id", "Desc": "variable"})
        .assign(
            description=lambda x: x["variable"].str[len(prefix) :],
            tablename="CAGDP2",
            dataset="Regional",
            line_code=lambda x: x["id"].astype(int),
        )
    )
    return df


class CountyGDP(OnConflictNothingBase):
    pk = '("id", "year", "fips")'
    table_name = "bea_gdp"

    def __init__(self, year):
        super().__init__()
        self.year = year

    def _insert_query(self, df, table_name, temp_name, pk):
        out = f"""
        INSERT INTO data.{table_name} (id, year, fips, value)
        SELECT bv.id, year, fips, value
        from {temp_name} tt
        LEFT JOIN meta.bea_variables bv using (dataset, tablename, line_code)
        INNER JOIN data.us_counties using(fips)
        ON CONFLICT {pk} DO UPDATE set value = excluded.value;
        """
        return textwrap.dedent(out)

    def get(self, concurrency=6):
        line_codes = [
            1,
            10,
            11,
            12,
            13,
            2,
            25,
            3,
            34,
            35,
            36,
            45,
            50,
            51,
            56,
            59,
            6,
            60,
            64,
            65,
            68,
            69,
            70,
            75,
            76,
            79,
            82,
            83,
            87,
            88,
            89,
            90,
            91,
            92,
        ]

        def _get_dataset(line_code):
            res = _make_bea_request(
                method="getdata",
                datasetname="regional",
                tablename="CAGDP2",
                geofips="county",
                year=self.year,
                linecode=line_code,
            )
            return pd.DataFrame(res["Results"]["Data"])

        def get_number(col):
            return pd.to_numeric(col, errors="coerce")

        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            dfs = pool.map(_get_dataset, line_codes)

        df = pd.concat(list(dfs), ignore_index=True)
        ds_id = df["Code"].str.extract(r"(?P<tablename>\w+)-(?P<line_code>\d+)")
        out = pd.concat([df, ds_id], axis=1).assign(
            value=lambda x: get_number(x["DataValue"].str.replace(",", "")),
            fips=lambda x: x["GeoFips"].astype(int),
            dataset="Regional",
            line_code=lambda x: x["line_code"].astype(int),
            year=lambda x: x["TimePeriod"].astype(int),
        )
        return out[["dataset", "tablename", "line_code", "year", "fips", "value"]]
