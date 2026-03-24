from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle



# Change from readonly to full calendar access
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def get_calendar_service():
    creds = None

    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build("calendar", "v3", credentials=creds)


def main():
    service = get_calendar_service()

    event = {
        "summary": "Handyman Appointment - John Smith",
        "location": "Customer Address Here",
        "description": "Ceiling fan installation quote and service visit.",
        "start": {
            "dateTime": "2026-03-23T13:00:00-05:00",
            "timeZone": "America/Chicago",
        },
        "end": {
            "dateTime": "2026-03-23T14:00:00-05:00",
            "timeZone": "America/Chicago",
        },
    }

    created_event = service.events().insert(
        calendarId="primary",
        body=event
    ).execute()

    print("Event created successfully.")
    print("Event ID:", created_event["id"])
    print("Event Link:", created_event.get("htmlLink"))


if __name__ == "__main__":
    main()