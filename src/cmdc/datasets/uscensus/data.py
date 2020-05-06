import json
import os
import pandas as pd
import requests


def _update_data_file(filename):
    "Saves the available datasets into a file called `filename`"
    url = "https://api.census.gov/data.json"
    available_data = requests.get(url)

    with open(filename, "w") as f:
        f.write(json.dumps(available_data.json()))


def _load_metadata(filename):
    "Loads the available datasets from a file called `filename`"
    if not os.path.isfile(filename):
        _update_data_file(filename)

    with open(filename, "r") as f:
        available_data = json.load(f)

    return available_data["dataset"]


AVAIL_DATASETS = _load_metadata("./available_data.json")
_ACS1_DATASETS = [x for x in AVAIL_DATASETS if "acs1" in x["c_dataset"]]
_ACS5_DATASETS = [x for x in AVAIL_DATASETS if "acs5" in x["c_dataset"]]


class USCensusBaseAPI(object):
    census_base_url = "https://api.census.gov/data/"

    def __init__(self, dataset, key):
        self.dataset = dataset
        self.key = key

        return None

    def determine_valid_geographies(self, geo_url):
        # TODO: This is a method so that in the future, we can pull the
        #       list of valid geographies from `dataset["c_geographyLink"]`
        #       rather than impose this small subset of geographies
        VALID_GEOGRAPHIES = {
            "us": "us:*",
            "region": "region:*",
            "division": "division:*",
            "state": "state:*",
            "county": "county:*",
            "msa": "metropolitan%20statistical%20area/micropolitan%20statistical%20area:*",
            "csa": "combined%20statistical%20area:*",
            "puma": "public%20use%20microdata%20area:*"
        }

        return VALID_GEOGRAPHIES

    def process_column_args(self, columns):
        """
        Takes the column arguments and turns them into a string that
        can be an input to a request

        Parameters
        ----------
        columns : list(str)
            The variables that should be retrieved from Census
        """
        # TODO: Validate the variable arguments
        if isinstance(columns, str):
            columns = [columns]

        return "&get=" + ",".join(columns)

    def process_geography_args(self, geography, geo_url=""):
        """
        Takes the geography arguments and turns them into a string
        that can be an input to a request

        Parameters
        ----------
        geography : dict, str, or tuple
            The relevant geography for the data. If `geography` is a
            string, it must be one of the values in `VALID_GEOGRAPHIES`
            and you will receive values for all of the corresponding
            geographies. If `geography` is a tuple then the first
            element should be a geography in `VALID_GEOGRAPHIES` and
            the second element should be a collection of values that
            are subsets of that geography. If `geography` is a dict, it
            should use have the keys `for` and `in` as described in the
            US Census documentation --- The values of these keys should
            be tuples with a geography as the first element and a
            collection of values as the second element as described
            above.
        """
        VALID_GEOGRAPHIES = self.determine_valid_geographies(geo_url)
        out=""

        if isinstance(geography, str):
            is_valid = geography in VALID_GEOGRAPHIES.keys()
            if not is_valid:
                msg = "If you pass a string, you must use one of the "
                msg += "geographies in the `VALID_GEOGRAPHIES` dict."
                raise ValueError(msg)

            out = "&for=" + VALID_GEOGRAPHIES[geography]

        elif isinstance(geography, dict):
            is_valid = ("for" in geography.keys() and "in" in geography.keys())
            if not is_valid:
                msg = "If you pass a dict, you must have keys 'for' and 'in'"
                raise ValueError(msg)

            out = "&for=" + geography["for"][0]
            out += ":" + ",".join(map(str, geography["for"][1]))
            out += "&in=" + geography["in"][0]
            out += ":" + ",".join(map(str, geography["in"][1]))

        elif isinstance(geography, tuple):
            is_valid = geography[0] in VALID_GEOGRAPHIES.keys()

            out = "&for=" + geography[0]
            out += ":" + ",".join(map(str, geography[1]))

        return out

    def _get(self, api_url, columns, geography):
        """
        This is the hidden get method that actually fetches the data
        from the US Census API.

        Parameters
        ----------
        api_url: str
            The api endpoint that the data is stored at
        columns : list(string)
            The data columns that you would like
        geography : str, dict, or tuple
            See documentation for `self.process_geography_args`
        """
        # Build up the request url
        req_url = api_url + f"?key={self.key}"
        req_url += self.process_column_args(columns)
        req_url += self.process_geography_args(geography)

        req = requests.get(req_url)

        return req

    def get(self, columns, geography, year):
        """
        This method should not be called on the Parent class
        `CensusBaseAPI`. It will error because it requires a
        `gen_api_url` method and a `valid_years` property both
        of which are only implemented at the dataset level

        Parameters
        ----------
        columns : list(string)
            The data columns that you would like
        geography : str, dict, or tuple
            See documentation for `self.process_geography_args`
        year : int
            The year the survey was collected. It
        """
        if not year in self.valid_years:
            msg = "Must be one of the years that the ACS can be collected"
            raise ValueError(msg)

        # Perform actual request
        api_url = self.gen_api_url(year)
        req = self._get(api_url, columns, geography)

        if req.status_code != 200:
            print(req.status_code)
            print(req.text)
            msg = "API request failed... See printout above for more info"
            raise ValueError(msg)
        req_json = req.json()

        # Store in a DataFrame
        df = pd.DataFrame(data=req_json[1:], columns=req_json[0])
        df[columns] = df[columns].apply(pd.to_numeric)

        return df


class ACS1(USCensusBaseAPI):
    """
    The American Community Survey (ACS) is an ongoing survey that
    provides data every year -- giving communities the current
    information they need to plan investments and services. The ACS
    covers a broad range of topics about social, economic, demographic,
    and housing characteristics of the U.S. population. Much of the ACS
    data provided on the Census Bureau's Web site are available
    separately by age group, race, Hispanic origin, and sex.

    The 1 year files incorporates a single year's worth of data
    collection and provides detailed information for areas with a
    population of more than 65,000.

    For more information, please refer to:
        * https://www.census.gov/data/developers/data-sets/acs-1year.html

    Parameters
    ----------
    key : string
        The US Census API key.
    """
    valid_years = set(x["c_vintage"] for x in _ACS1_DATASETS)

    def __init__(self, key):
        super(ACS1, self).__init__(dataset="acs1", key=key)

    def gen_api_url(self, year):
        return self.census_base_url + f"{year}/acs/acs1"


class ACS5(USCensusBaseAPI):
    """
    The American Community Survey (ACS) is an ongoing survey that
    provides data every year -- giving communities the current
    information they need to plan investments and services. The ACS
    covers a broad range of topics about social, economic, demographic,
    and housing characteristics of the U.S. population. Much of the ACS
    data provided on the Census Bureau's Web site are available
    separately by age group, race, Hispanic origin, and sex.

    The 5 year files incorporates five year's worth of data into it's
    estimates and provides detailed information for all census areas
    down to the census block level.

    For more information, please refer to:
        * https://www.census.gov/data/developers/data-sets/acs-5year.html

    Parameters
    ----------
    key : string
        The US Census API key.
    """
    valid_years = set(x["c_vintage"] for x in _ACS5_DATASETS)

    def __init__(self, key):
        super(ACS5, self).__init__(dataset="acs5", key=key)

    def gen_api_url(self, year):
        return self.census_base_url + f"{year}/acs/acs5"

