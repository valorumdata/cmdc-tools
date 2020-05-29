#%%
import requests
import pathlib

BASE_URL = "https://api.covid.valorum.ai"


class Request(object):
    def __init__(self, client, path, parameters):
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
        pass

    def __call__(self, **filters):
        # process filters
        filter_names = [x["name"] for x in self.valid_filters]
        filtered = []
        for name, val in filters.items():
            # TODO: add validation of parameter type
            if name not in filter_names:
                msg = (
                    f"{self.path} path given filter {name}. "
                    f"Valid filters are {', '.join(filter_names)}"
                )
                raise ValueError(msg)

        self.client.add_request(self.path, filters)

        return self.client

    def __repr__(self):
        filter_names = [x["name"] for x in self.valid_filters]
        msg = (
            f"Request builder for {self.path} endpoint"
            f"\nValid filters are {', '.join(filter_names)}"
        )
        return msg


class Client(object):
    def __init__(self):
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
            self._key = f.read()

        return self._key

    @key.setter
    def key(self, x):
        if x is not None:
            self.sess.headers.update({"apikey": x})
            with open(self._keypath, "w") as f:
                f.write(x)
        self._key = x

    def register(self):
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
        home = pathlib.Path.home()
        keyfile = home / ".cmdc" / "apikey"
        keyfile.parent.mkdir(parents=True, exist_ok=True)
        return keyfile

    ## Requests
    def _unionize_filters(self):
        all_filters = {}
        for path, filts in self._current_request.items():
            for k, v in filts.items():
                if k in all_filters:
                    current = all_filters[k]
                    if current != v:
                        msg = (
                            f"Found conflicting values for common filter {k}. "
                            "Found both {v} and {current}"
                        )
                        raise ValueError(msg)
                else:
                    all_filters[k] = v

        return all_filters

    def fetch(self):
        self._current_request = {}
        self._current_request_headers = {}

        return

    ## Dynamic query builder
    def __getattr__(self, ds):
        if not ds in dir(self):
            msg = f"Unknown dataset {ds}. Known datasets are {dir(self)}"
            raise ValueError(msg)

        route = self._spec["paths"]["/" + ds]["get"]
        return Request(self, ds, route["parameters"])

    def __dir__(self):
        paths = self._spec["paths"]
        return [x.strip("/") for x in paths if x != "/"]

    def __repr__(self):
        out = "CMDC Client"

        if len(self._current_request) > 0:
            out += ". Current request:\n  -"
            req_desc = [f"{k}: {v}" for k, v in self._current_request.items()]
            out += "\n  -".join(req_desc)

        return out

    def add_request(self, path, filters):
        self._current_request.update({path: filters})


# %%
if __name__ == "__main__":
    c = Client()
    c.economics(fips=12).demographics()
