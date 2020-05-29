#%%
import requests
import pathlib
import urllib
from typing import Dict, List, Any

import pandas as pd

BASE_URL = "https://api.covid.valorum.ai"


class Request(object):
    """
    Internal class to be used when building up a request
    """

    def __init__(self, client: "Client", path: str, parameters: Dict[str, List]):
        """
        Create a Request builder object

        Parameters
        ----------
        client: Client
            The API Client that should be returned after calling an instance of
            this class
        path: string
            The API path for which the Request will be built
        parameters: Dict[str, List]
            A list of OpenAPI 2.0 parameters for this endpoint
        """
        self.path = path
        self.client = client
        self.parameters = parameters
        self.valid_filters = []
        for p in parameters:
            if isinstance(p, dict) and len(p) == 1 and "$ref" in p:
                # look up parameter
                param = list(p.values())[0]
                prefix = "#/parameters/"
                assert param.startswith(prefix)

                self.valid_filters.append(
                    client._spec["parameters"][param.replace(prefix, "")]
                )

        self.filter_names = [x["name"] for x in self.valid_filters]
        pass

    def has_filter(self, param: str) -> bool:
        """
        Check if `param` is a valid parameter for this endpoint
        """
        return param in self.filter_names

    def __call__(self, **filters) -> "Client":
        """
        Validate a given set of query parameters and confirm they are applicable
        for this endpoint
        """
        # process filters
        filtered = []
        for name, val in filters.items():
            # TODO: add validation of parameter type
            if not self.has_filter(name):
                msg = (
                    f"{self.path} path given filter {name}. "
                    f"Valid filters are {', '.join(self.filter_names)}"
                )
                raise ValueError(msg)

        self.client.add_request(self.path, filters)

        return self.client

    def __repr__(self) -> str:
        filter_names = [x["name"] for x in self.valid_filters]
        msg = (
            f"Request builder for {self.path} endpoint"
            f"\nValid filters are {', '.join(filter_names)}"
        )
        return msg


def create_filter_rhs(x: str) -> str:
    """
    Parse the string `x` to be a postgrest accepted string for filtering
    rows
    """
    # TODO: handle more than just eq
    return f"eq.{x}"


class Client(object):
    def __init__(self):
        """
        API Client for the CMDC database

        Examples
        --------

        Construct a client:

        ```python
        >>> c = Client()
        ```

        Use the client to request an API key (will be prompted for email address)

        ```ipython
        c.register()
        ```

        Build a dataset for Orange County, Florida:

        ```ipython
        # TODO: implement these docs
        ```

        """
        self._current_request = {}
        self._current_request_headers = {}
        self._key = None
        self.sess = requests.Session()
        res = self.sess.get(BASE_URL + "/swagger.json")
        if not res.ok:
            raise ValueError("Could not request the API structure -- try again!")
        self._spec = res.json()

        if self.key is None:
            msg = (
                "No API key found. Please request a "
                "free API key by calling the `register` method"
            )
            print(msg)

        pass

    ## API key handling
    @property
    def key(self):
        # already loaded -- return
        if self._key is not None:
            return self._key

        # try to load
        keyfile = self._keypath
        if not keyfile.is_file():
            return None
        with open(keyfile, "r") as f:
            self.key = f.read()

        return self._key

    @key.setter
    def key(self, x):
        if x is not None:
            self.sess.headers.update({"apikey": x})
            with open(self._keypath, "w") as f:
                f.write(x)
        self._key = x

    def register(self) -> str:
        from email_validator import validate_email, EmailNotValidError

        msg = "Please provide an email address to request a free API key: "
        email = input(msg)

        try:
            valid = validate_email(email)
            email = valid.email
        except EmailNotValidError as e:
            raise e

        res = requests.post(BASE_URL + "/auth", data=dict(email=email))

        if not res.ok:
            msg = f"Could not request api key. Message from server: {res.content}"
            raise ValueError(msg)

        self.key = res.json()["key"]
        print("The API key has been saved and will be used in future sessions")

        return self.key

    @property
    def _keypath(self):
        """
        Path to the file with the user's apikey. Makes sure parent directory
        exists
        """
        home = pathlib.Path.home()
        keyfile = home / ".cmdc" / "apikey"
        keyfile.parent.mkdir(parents=True, exist_ok=True)
        return keyfile

    ## Requests
    def _unionize_filters(self) -> Dict[str, Dict[str, str]]:
        """
        Process filters built up in request. Rules are:

        - If the name of the filter is `variable` it is applied request by
          request. Thus different endpoints can have different values for the
          `variables` filter
        - If the name of the filter is anything else (e.g. vintage, fips, dt,
          meta_date), it is applied to ALL requests

        While processing the common filters, if the value passed in any two
        parts of the request builder are not the same, a ValueError will be
        thrown. For example,

        ```ipython
        c = Client()
        c.economics(fips=12095).demographics(fips=4013)
        c._unionize_filters()
        ```

        Would be an error

        The return value is a dictionary mapping query paths to the filters
        that apply to that request
        """
        common_filters = {}
        out = {}
        # for each request
        for path, filts in self._current_request.items():
            out[path] = {}

            # for each filter in this request
            for filt_name, filt_val in filts.items():
                # if the filter is for `variable` pass it through directly and
                # do not add it to common_filters
                if filt_name == "variable":
                    out[path][filt_name] = filt_val

                    continue

                # if we have seen this filter, check to make sure we don't have
                # conflicting values
                if filt_name in common_filters:
                    current = common_filters[filt_name]
                    if current != filt_val:
                        msg = (
                            f"Found conflicting values for common "
                            f"filter {filt_name}. "
                            f"Found both {filt_val} and {current}"
                        )
                        raise ValueError(msg)
                else:
                    # add this value to the common_filters tracker
                    common_filters[filt_name] = filt_val

        # for each request, add in common filters that apply
        for path in out.keys():
            for filt_name, filt_val in common_filters.items():
                if self.__getattr__(path).has_filter(filt_name):
                    out[path][filt_name] = filt_val

        return out

    def _create_query_string(self, path: str, filters: Dict[str, Any]) -> str:
        """
        Given a path and filters to apply to that path, construct a query string
        """
        prepped_filters = {k: create_filter_rhs(v) for k, v in filters.items()}
        query = BASE_URL + "/" + path
        if len(prepped_filters) > 0:
            query += "?" + urllib.parse.urlencode(prepped_filters)

        return query

    def _url_to_df(self, url: str) -> pd.DataFrame:
        "Make GET request to `url` and parse resulting JSON as DataFrame"
        res = self.sess.get(url)
        if not res.ok:
            raise ValueError(f"Error fetching {url}: {res.content}")
        return pd.DataFrame(res.json())

    def _reshape_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Reshape a DataFrame from long to wide form, adhering to the following
        rules:

        - If the `meta_date` column exists, replace `variable` column with
          {variable}_{meta_date} and then drop `meta_date`
        - Construct a pivot_table where the columns come from the `variable`
          column, values come from the `value` column, and all other columns are
          used as an index
        """
        if df.shape[0] == 0:
            # empty dataframe
            return df

        cols = list(df)
        for c in ["variable", "value"]:
            if c not in cols:
                raise ValueError(
                    f"Column {c} not found in DataFrame. Please report a bug"
                )
        if "meta_date" in cols:
            if "variable" in cols:
                df["variable"] = (
                    df["variable"].astype(str) + "_" + df["meta_date"].astype(str)
                )
                df.drop("meta_date", axis=1)

        idx = list(set(cols) - set(["variable", "value"]))
        return df.pivot_table(index=idx, columns="variable", values="value")

    def _run_queries(self, urls: Dict[str, str]) -> Dict[str, pd.DataFrame]:
        """
        Transform a dict mapping paths to request urls, to a dict mapping paths
        to DataFrames with the result of GETting the url
        """
        # TODO: optimize and make async
        return {k: self._url_to_df(v) for k, v in urls.items()}

    def _combine_dfs(self, dfs: List[pd.DataFrame]) -> pd.DataFrame:
        """
        Merge all `dfs` on common columns (typically in the index)
        """
        out = dfs[0]
        for right in dfs[1:]:
            out = out.merge(right)
        return out

    def fetch(self) -> pd.DataFrame:
        filters = self._unionize_filters()
        query_strings = {k: self._create_query_string(k, v) for k, v in filters.items()}
        dfs = self._run_queries(query_strings)
        wide_dfs = [self._reshape_df(v) for v in dfs.values()]
        output = self._combine_dfs(wide_dfs)

        self._current_request = {}
        self._current_request_headers = {}

        return output

    ## Dynamic query builder
    def __getattr__(self, ds: str) -> Request:
        if not ds in dir(self):
            msg = f"Unknown dataset {ds}. Known datasets are {dir(self)}"
            raise ValueError(msg)

        route = self._spec["paths"]["/" + ds]["get"]
        return Request(self, ds, route["parameters"])

    def __dir__(self) -> List[str]:
        paths = self._spec["paths"]
        return [x.strip("/") for x in paths if x != "/"]

    def __repr__(self) -> str:
        out = "CMDC Client"

        if len(self._current_request) > 0:
            out += ". Current request:\n  -"
            req_desc = [f"{k}: {v}" for k, v in self._current_request.items()]
            out += "\n  -".join(req_desc)

        return out

    def add_request(self, path: str, filters: Dict[str, Any]) -> None:
        self._current_request.update({path: filters})


# %%
if __name__ == "__main__":
    c = Client()
    c.economics(
        meta_date="2018-01-01", variable="GDP_All industry total"
    ).demographics()
