import geopandas as gpd
import pandas as pd

from ..base import InsertWithTempTable, DatasetBaseNoDate
from .census import STATE_FIPS


BASE_GEO_URL = "https://www2.census.gov/geo/tiger/"


def _create_fips(geo: str, df: pd.DataFrame):
    """
    Converts geographic columns into a fips code

    Parameters
    ----------
    df : pd.DataFrame
        The output of a `data_get` request and must include the
        relevant geographic columns

    Returns
    -------
    df : pd.DataFrame
        A DataFrame with the fips code values included and the
        other geographic columns dropped
    """
    if geo == "state":
        df["fips"] = df["state"].astype(int)
        df["county"] = "000"
    elif geo == "county":
        df["fips"] = df["state"].astype(int) * 1_000 + df["county"].astype(int)
    else:
        raise ValueError("Only state/county are supported")

    return df


def _download_shape_file(apiurl: str, filename: str):
    # Create the url string geopandas needs to know that
    # it is a zip file
    rq_str = f"{apiurl}{filename}.zip"

    # Read shapefile
    gdf = gpd.read_file(rq_str)

    gdf = gdf.rename(
        columns={"STATEFP": "STATE", "COUNTYFP": "COUNTY", "TRACTCE": "TRACT"}
    )
    gdf["INTPTLAT"] = pd.to_numeric(gdf["INTPTLAT"])
    gdf["INTPTLON"] = pd.to_numeric(gdf["INTPTLON"])
    gdf.columns = [c.lower() for c in gdf.columns]

    return gdf


def download_shape_files(geo: str, year: int):
    """
    Downloads the shape files for a particular geography and year.

    The code currently only accepts state, county, and tract as the
    possible values for `geo`

    Parameters
    ----------
    geo : str
        The geography to download
    year : int
        The year of geography definitions to reference

    Returns
    -------
    gdf : pandas.DataFrame
        A DataFrame with information about the specified geography
    """
    geo = geo.lower()
    url = BASE_GEO_URL + f"TIGER{year}/{geo.upper()}/"

    datafile = f"tl_{year}_us_{geo}"
    gdf = _download_shape_file(url, datafile)
    gdf = _create_fips(geo, gdf)

    if "namelsad" not in gdf.columns:
        gdf["namelsad"] = gdf["name"].copy()

    keep = [
        "fips",
        "state",
        "county",
        "name",
        "namelsad",
        "aland",
        "intptlat",
        "intptlon",
    ]
    gdf = gdf.loc[:, keep]
    gdf.loc[:, "namelsad"] = gdf.loc[:, "namelsad"].str.replace("city", "City")

    # Convert land area to square miles (m^2 -> km^2 -> mi^2
    gdf["aland"] = (gdf["aland"] / 1_000_000) / 2.5899

    gdf = gdf.rename(
        columns={
            "aland": "area",
            "intptlat": "latitude",
            "intptlon": "longitude",
            "namelsad": "fullname",
        }
    )

    return gdf


class USGeoBaseAPI(InsertWithTempTable, DatasetBaseNoDate):
    table_name = "us_fips"
    pk = '("id")'
    autodag = False

    def __init__(self, geo: str = "state", year: int = 2019):
        self.geo = geo
        self.year = year

    def _insert_query(self, df: pd.DataFrame, table_name: str, temp_name: str, pk: str):
        _sql_geo_insert = f"""
        INSERT INTO meta.{table_name} (fips, state, county, name, fullname, area, latitude, longitude)
        SELECT fips, state, county, name, fullname, area, latitude, longitude FROM {temp_name}
        ON CONFLICT (fips) DO UPDATE
          SET
            name=EXCLUDED.name,
            fullname=EXCLUDED.fullname
        ;
        """

        return _sql_geo_insert

    def get(self):
        return download_shape_files(self.geo, self.year)


# class USGeoUnknownCounties(InsertWithTempTable, DAtasetBaseNoDate):
#     table_name = "us_fips"
#     pk = '("id")'
#
#     def __init__(self):
#         super(USGeoUnknownCounties, self).__init__()
#
#     def _insert_query(self, df, table_name, temp_name, pk):
#         _sql_unkcounty_insert = f"""
#         WITH unkwn AS (
#             SELECT 1000*fips + 999 as fips, 'Unknown' as name
#             FROM meta.us_fips WHERE fips<100
#         )
#         INSERT INTO meta.us_fips (fips, name)
#         SELECT fips, name FROM unkwn
#         ON CONFLICT (fips) DO UPDATE SET fips=EXCLUDED.fips, name=EXCLUDED.name
#         """
#         return _sql_unkcounty_insert
