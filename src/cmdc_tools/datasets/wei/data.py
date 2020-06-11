import io
import os
import pandas as pd
import pickle
import pathlib

from .. import InsertWithTempTable, DatasetBaseNoDate
from googleapiclient.discovery import build, Resource
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Default values for credential and token files
CRED_FILE = pathlib.Path.home() / ".cmdc" / "google_credentials.json"
TOKEN_FILE = pathlib.Path.home() / ".cmdc" / "google_token.pickle"


def create_gdrive_service(
    cred_fn: str = "credentials.json", token_fn: str = "token.pickle"
):
    """
    Creates a google drive api service that can be used to query and
    download particular files

    Parameters
    ----------
    cred_fn : str
        The filename where the api credentials are stored
    token_fn : str
        The filename where the OAuth token is stored

    Returns
    -------
    service : googleapiclient.discovery.Resource
        The google drive api resource
    """
    creds = None
    SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

    # Check for whether we already have a token
    if os.path.exists(token_fn):
        with open(token_fn, "rb") as token:
            creds = pickle.load(token)

    # If the token doesn't exist or is no longer valid, create a new
    # one by either refreshing the existing one or re-validating
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(cred_fn, SCOPES)
            creds = flow.run_local_server(port=0)

            with open(token_fn, "wb") as token:
                pickle.dump(creds, token)

    service = build("drive", "v3", credentials=creds)

    return service


def retrieve_spreadsheet(service: Resource, fileId: str):
    """
    Helper function that can fetch a (bytes) file from Google Drive

    Parameters
    ----------
    service : googleapiclient.discovery.Resource
        The google drive api resource
    fileId : str
        The file id

    Returns
    -------
    out : io.BytesIO
        An io.BytesIO file that contains the file downloaded from
        Google Drive
    """

    # Get reference to particular file
    file_ref = service.files().get_media(fileId=fileId)

    # Fetch the file
    out = io.BytesIO(file_ref.execute())

    return out


class WEI(InsertWithTempTable, DatasetBaseNoDate):
    """
    The weekly economic index (WEI) is an index developed and
    published by Jim Stock. It can be found online on his blog at
    https://www.jimstock.org/ --- The description of the data
    that follows comes from his blog.

    The WEI is a composite of 6 weekly economic indicators:
      * Redbook same-store sales
      * Rasmussen Consumer Confidence
      * new claims for unemployment insurance
      * the American Staffing Association Staffing Index
      * steel production
      * wholesale sales of gasoline, diesel, and jet fuel

    All series are represented as year-over-year percentage changes.
    These series are combined into a single index of weekly economic
    activity. The index closely tracks monthly industrial production
    and quarterly GDP. Of these six series, five are available by
    Thursday morning for the week ending the previous Saturday.
    """

    fileId = "192MTTC1Tqol_LLgF-00R7-2c8jel-QmV"
    pk = '("date")'
    table_name = "weeklyeconomicindex"

    def __init__(self, cred_fn: str = CRED_FILE, token_fn: str = TOKEN_FILE):
        self.cred_fn = cred_fn
        self.token_fn = token_fn

    def get(self):
        """
        Fetches and updates the weekly economic index published by Jim
        Stock on his website at https://www.jimstock.org/

        Returns
        -------
        wei : pd.DataFrame
            A DataFrame that contains the weekly economic index
        """

        # Create google drive api service
        service = create_gdrive_service(cred_fn=self.cred_fn, token_fn=self.token_fn)

        # Fetch file as bytesIO and then read into pandas
        wei_file = retrieve_spreadsheet(service, self.fileId)
        wei = pd.read_excel(wei_file)

        # Rename columns and set country value in case we add other
        # countries in the future
        wei = wei.rename(columns={"Date": "dt", "WEI": "wei"})

        return wei
