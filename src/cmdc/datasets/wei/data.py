import io
import os
import pandas as pd
import pickle

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def create_gdrive_service(cred_fn="credentials.json", token_fn="token.pickle"):
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
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

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
            flow = InstalledAppFlow.from_client_secrets_file(
                cred_fn, SCOPES
            )
            creds = flow.run_local_server(port=0)

            with open(token_fn, "wb") as token:
                pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)

    return service


def retrieve_spreadsheet(service, fileId):
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


def update_WEI():
    """
    Fetches and updates the weekly economic index published by Jim
    Stock on his website at https://www.jimstock.org/

    Returns
    -------
    wei : pd.DataFrame
        A DataFrame that contains the weekly economic index
    """
    service = create_gdrive_service(
        cred_fn="./conf/local/google_credentials.json",
        token_fn="./conf/local/google_token.pickle"
    )
    wei_file = retrieve_spreadsheet(service, "192MTTC1Tqol_LLgF-00R7-2c8jel-QmV")
    wei = pd.read_excel(wei_file)

    wei = wei.rename(columns={"Date": "date", "WEI": "wei"})
    wei["country"] = "US"

    return wei

