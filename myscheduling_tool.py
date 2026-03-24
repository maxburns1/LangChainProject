import pickle
import json
import os
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta, time
from langchain.tools import tool
from zoneinfo import ZoneInfo

tz = ZoneInfo("America/Chicago")

# ---------------------------
# GOOGLE CALENDAR CONFIG
# ---------------------------
CALENDAR_READ_SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
CALENDAR_WRITE_SCOPES = ["https://www.googleapis.com/auth/calendar"]
CALENDAR_ID = "primary"
TIMEZONE = "America/Chicago"



def get_calendar_service(write_access: bool = False):
    scopes = CALENDAR_WRITE_SCOPES
    token_file = "token.pickle"

    creds = None
    if os.path.exists(token_file):
        with open(token_file, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                scopes
            )
            creds = flow.run_local_server(port=0)

        with open(token_file, "wb") as token:
            pickle.dump(creds, token)

    return build("calendar", "v3", credentials=creds)

#Convert weekday name to the next actual date
def parse_next_weekday(requested_day: str):
    weekdays = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }

    requested_day = requested_day.strip().lower()
    if requested_day not in weekdays:
        raise ValueError(f"Unsupported day: {requested_day}")

    today = datetime.now()
    target = weekdays[requested_day]
    days_ahead = (target - today.weekday()) % 7

    if days_ahead == 0:
        days_ahead = 7

    return (today + timedelta(days=days_ahead)).date()


#Define time windows
def get_time_window_bounds(time_window: str):
    time_window = time_window.strip().lower()

    if time_window == "morning":
        return time(9, 0), time(12, 0)
    elif time_window == "afternoon":
        return time(12, 0), time(17, 0)
    elif time_window == "evening":
        return time(17, 0), time(20, 0)
    else:
        return time(9, 0), time(17, 0)
    

# ===========================
# CALENDAR AVAILABILITY
# ===========================
#Google’s freebusy.query method returns busy intervals for the calendars you specify.


def get_busy_periods(calendar_service, start_dt: datetime, end_dt: datetime, calendar_id: str = "primary"):
    body = {
        "timeMin": start_dt.isoformat(),
        "timeMax": end_dt.isoformat(),
        "items": [{"id": calendar_id}]
    }

    result = calendar_service.freebusy().query(body=body).execute()

    busy_ranges = result["calendars"][calendar_id]["busy"]

    busy = []
    for block in busy_ranges:
        busy_start = datetime.fromisoformat(block["start"].replace("Z", "+00:00")).replace(tzinfo=None)
        busy_end = datetime.fromisoformat(block["end"].replace("Z", "+00:00")).replace(tzinfo=None)
        busy.append((busy_start, busy_end))

    return busy

def compute_open_slots(
    start_dt: datetime,
    end_dt: datetime,
    busy_periods,
    duration_minutes: int = 60,
    step_minutes: int = 30
):
    """
    Walk through the requested window in increments and keep any slot
    that does not overlap a busy calendar block.
    """
    slots = []
    cursor = start_dt

    while cursor + timedelta(minutes=duration_minutes) <= end_dt:
        slot_end = cursor + timedelta(minutes=duration_minutes)

        overlaps = any(
            not (slot_end <= busy_start or cursor >= busy_end)
            for busy_start, busy_end in busy_periods
        )

        if not overlaps:
            slots.append(cursor)

        cursor += timedelta(minutes=step_minutes)

    return slots


def format_slots(slots, max_results: int = 5):
    """
    Convert datetime slot objects into numbered user-friendly display text
    and machine-friendly ISO strings.
    """
    formatted = []

    for i, slot in enumerate(slots[:max_results], start=1):
        formatted.append({
            "option_number": i,
            "display": slot.strftime("%A %I:%M %p"),
            "start_iso": slot.isoformat()
        })

    return formatted


# ===========================
# LANGCHAIN TOOL
# ===========================
@tool
def scheduling_tool(
    requested_day: str,
    time_window: str = "afternoon",
    duration_minutes: int = 60
) -> str:
    """
    Find available appointment slots in Google Calendar that best match the requested day and time window.

    Use this tool when the user asks for availability, appointment times, or scheduling options.
    Returns JSON containing the best matching open slots.
    """
    try:
        calendar_service = get_calendar_service()

        target_date = parse_next_weekday(requested_day)
        window_start, window_end = get_time_window_bounds(time_window)

        tz = ZoneInfo(TIMEZONE)

        start_dt = datetime.combine(target_date, window_start, tzinfo=tz)
        end_dt = datetime.combine(target_date, window_end, tzinfo=tz)

        busy_periods = get_busy_periods(calendar_service, start_dt, end_dt)
        open_slots = compute_open_slots(
            start_dt=start_dt,
            end_dt=end_dt,
            busy_periods=busy_periods,
            duration_minutes=duration_minutes,
            step_minutes=30
        )

        if not open_slots:
            result = {
                "requested_day": requested_day,
                "time_window": time_window,
                "duration_minutes": duration_minutes,
                "available_slots": [],
                "message": f"No open {time_window} slots found for {requested_day}."
            }
            return json.dumps(result, indent=2)

        formatted_slots = format_slots(open_slots, max_results=5)

        result = {
            "requested_day": requested_day,
            "time_window": time_window,
            "duration_minutes": duration_minutes,
            "available_slots": formatted_slots,
            "message": f"Best available {time_window} slots for {requested_day} were found."
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        error_result = {
            "requested_day": requested_day,
            "time_window": time_window,
            "duration_minutes": duration_minutes,
            "available_slots": [],
            "message": f"Scheduling tool error: {str(e)}"
        }
        return json.dumps(error_result, indent=2)
    

result = scheduling_tool.invoke({
    "requested_day": "Friday",
    "time_window": "morning",
    "duration_minutes": 60
})

#print(result)