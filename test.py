"""
Run this once to see all your Google calendars and their IDs.
Copy the correct calendar ID into uv_google.py
"""
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
 
SCOPES = ["https://www.googleapis.com/auth/calendar"]
TOKEN_FILE = "token.json"
CREDENTIALS_FILE = "credentials.json"
 
creds = None
if os.path.exists(TOKEN_FILE):
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
 
service = build("calendar", "v3", credentials=creds)
calendars = service.calendarList().list().execute()
 
print("\nYour Google Calendars:\n")
for cal in calendars.get("items", []):
    print(f"  Name: {cal['summary']}")
    print(f"  ID:   {cal['id']}")
    print()