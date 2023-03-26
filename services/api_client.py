import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

from config.settings import SCOPES, API_KEY, CREDENTIALS_FILE_PATH


class GoogleApiService:

    def __init__(self):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE_PATH, SCOPES)
        self.api_key: str = API_KEY
        self.auth = credentials.authorize(httplib2.Http())

    def get_sheets_service_simple(self):
        return build('sheets', 'v4', developerKey=self.api_key)

    def get_sheets_service(self):
        return build('sheets', 'v4', http=self.auth)

    def get_drive_service(self):
        return build('drive', 'v3', http=self.auth)
