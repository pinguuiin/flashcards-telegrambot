from googleapiclient.discovery import build
from google.oauth2 import service_account
import json

rowNumbers = 10000
RANGE_NAME = f'Sheet1!A1:J{rowNumbers}'
SPREADSHEET_ID = "1UQxRx-c_DmdZ2ZYuVtj5XhT4AxKf2hiC_fKoHK6gufA" # Test
KEY_FILE = "finnish-words-433909-600da906558d.json" # Oauth key here

with open(KEY_FILE, 'r') as source:
    cred_info = json.load(source)
creds = service_account.Credentials.from_service_account_info(cred_info)
# Connecting to the Spreadsheet

def authenticate_sheets():
    service = build('sheets', 'v4', credentials=creds)
    return service.spreadsheets()

sheets = authenticate_sheets()
result = sheets.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()