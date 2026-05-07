from dotenv import load_dotenv
load_dotenv()

from mycalendar_booking_tool import create_calendar_event_tool

print("=" * 60)
print("TEST: Create a test detailing appointment")
print("=" * 60)

result = create_calendar_event_tool.invoke({
    "customer_name": "Test Customer",
    "service_type": "interior detail",
    "start_iso": "2026-05-08T09:00:00-05:00",
    "duration_minutes": 60,
    "location": "123 Test Drive",
    "notes": "Test booking — feel free to delete. 2022 Honda Civic."
})
print(result)