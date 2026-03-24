from langchain.tools import tool
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from datetime import datetime, timedelta
import os
import pickle
import json

# ---------------------------
# GOOGLE CALENDAR CONFIG
# ---------------------------
CALENDAR_WRITE_SCOPES = ["https://www.googleapis.com/auth/calendar"]
CALENDAR_ID = "primary"
TIMEZONE = "America/Chicago"


# ===========================
# AUTH / SERVICE SETUP
# ===========================
def get_calendar_service():
    """
    Authenticate and return a Google Calendar service object with write access.
    Uses OAuth desktop credentials from credentials.json and stores the token locally.
    """
    creds = None
    token_file = "token.pickle"

    if os.path.exists(token_file):
        with open(token_file, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                CALENDAR_WRITE_SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(token_file, "wb") as token:
            pickle.dump(creds, token)

    return build("calendar", "v3", credentials=creds)


# ===========================
# LANGCHAIN TOOL
# ===========================
@tool
def create_calendar_event_tool(
    customer_name: str,
    service_type: str,
    start_iso: str,
    duration_minutes: int = 60,
    location: str = "",
    notes: str = ""
) -> str:
    """
    Create a Google Calendar event for a confirmed handyman appointment.

    Use this tool only after the user has clearly confirmed a specific appointment time.
    The start_iso must be a full ISO datetime string, such as:
    2026-03-20T10:30:00-05:00
    """
    try:
        calendar_service = get_calendar_service()

        start_dt = datetime.fromisoformat(start_iso)
        end_dt = start_dt + timedelta(minutes=duration_minutes)

        event = {
            "summary": f"Handyman Appointment - {customer_name}",
            "location": location,
            "description": (
                f"Customer: {customer_name}\n"
                f"Service: {service_type}\n"
                f"Notes: {notes}"
            ),
            "start": {
                "dateTime": start_dt.isoformat(),
                "timeZone": TIMEZONE
            },
            "end": {
                "dateTime": end_dt.isoformat(),
                "timeZone": TIMEZONE
            }
        }

        created_event = calendar_service.events().insert(
            calendarId=CALENDAR_ID,
            body=event
        ).execute()

        result = {
            "status": "success",
            "customer_name": customer_name,
            "service_type": service_type,
            "start_iso": start_dt.isoformat(),
            "end_iso": end_dt.isoformat(),
            "event_id": created_event.get("id"),
            "event_link": created_event.get("htmlLink", ""),
            "message": (
                f"Calendar event created successfully for {customer_name} "
                f"on {start_dt.strftime('%A %B %d, %Y at %I:%M %p')}."
            )
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        error_result = {
            "status": "error",
            "customer_name": customer_name,
            "service_type": service_type,
            "start_iso": start_iso,
            "message": f"Calendar booking error: {str(e)}"
        }
        return json.dumps(error_result, indent=2)
    

'''
result = create_calendar_event_tool.invoke({
    "customer_name": "John Smith",
    "service_type": "ceiling fan installation",
    "start_iso": "2026-03-20T10:30:00-05:00",
    "duration_minutes": 60,
    "location": "Customer Home",
    "notes": "Customer requested morning appointment."
})

print(result)
'''