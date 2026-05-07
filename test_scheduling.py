from dotenv import load_dotenv
load_dotenv()

from myscheduling_tool import scheduling_tool

print("=" * 60)
print("TEST: Find Friday morning slots")
print("=" * 60)
result = scheduling_tool.invoke({
    "requested_day": "Friday",
    "time_window": "morning",
    "duration_minutes": 60
})
print(result)

print("\n" + "=" * 60)
print("TEST: Find Monday afternoon slots")
print("=" * 60)
result = scheduling_tool.invoke({
    "requested_day": "Monday",
    "time_window": "afternoon",
    "duration_minutes": 60
})
print(result)