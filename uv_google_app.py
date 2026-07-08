from __future__ import print_function
import os
import os.path
import pytz
from datetime import datetime, time, timedelta
from uv_app import get_uv_for_training
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]

CALENDAR_ID = "n5tk9ds5ab72nk3hvm4i80mmm8@group.calendar.google.com"          # or your specific calendar ID
KEYWORDS = ["ball", "om"]        # event must contain all of these words
TOKEN_FILE = "oliver_token.json"
CREDENTIALS_FILE = "credentials.json"


def load_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
    return creds


def get_todays_trainings(service):
    adelaide = pytz.timezone("Australia/Adelaide")
    now = datetime.now(adelaide)

    start_of_day = adelaide.localize(datetime.combine(now.date(), time.min))
    end_of_day = adelaide.localize(datetime.combine(now.date(), time.max))

    events_result = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=start_of_day.isoformat(),
        timeMax=end_of_day.isoformat(),
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    trainings = []
    for event in events_result.get("items", []):
        summary = event.get("summary", "").lower()
        if all(k in summary for k in KEYWORDS):
            start_raw = event["start"].get("dateTime", event["start"].get("date"))
            end_raw = event["end"].get("dateTime", event["end"].get("date"))
            trainings.append({
                "summary": event.get("summary", "No title"),
                "start": datetime.fromisoformat(start_raw.replace("Z", "+00:00")),
                "end": datetime.fromisoformat(end_raw.replace("Z", "+00:00")),
                "id": event["id"]
            })
    print(start_of_day)
    return trainings


def create_uv_events(service, trainings):
    for t in trainings:
        warmup_start = t["start"] - timedelta(minutes=30)
        uv = get_uv_for_training(warmup_start, t["end"])

        uv_start = round(uv["uv_start"], 1)
        uv_end = round(uv["uv_end"], 1)
        title = f"UV Summary: {uv_start} → {uv_end}"

        event_body = {
            "summary": title,
            "start": {"dateTime": t["start"].isoformat()},
            "end": {"dateTime": t["end"].isoformat()},
        }

        service.events().insert(calendarId="primary", body=event_body).execute()
        print(f"Created: {title}")


def main():
    creds = load_credentials()
    service = build("calendar", "v3", credentials=creds)

    trainings = get_todays_trainings(service)

    if not trainings:
        print("No training sessions found for today.")
        return

    print(f"\nFound {len(trainings)} training session(s):\n")
    for t in trainings:
        print(f"  - {t['summary']}: {t['start'].strftime('%I:%M %p')} → {t['end'].strftime('%I:%M %p')}")

    create_uv_events(service, trainings)


if __name__ == "__main__":
    main()