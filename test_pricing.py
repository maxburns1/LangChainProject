from dotenv import load_dotenv
load_dotenv()

from mypricing_tool import pricing_tool

# Test 1: simple request
print("=" * 60)
print("TEST 1: Basic exterior wash")
print("=" * 60)
result = pricing_tool.invoke({"client_request": "How much for an exterior wash?"})
print(result)

# Test 2: urgency keyword
print("=" * 60)
print("TEST 2: Urgent interior detail")
print("=" * 60)
result = pricing_tool.invoke({"client_request": "I spilled coffee all over my interior, can someone come ASAP for a detail?"})
print(result)

# Test 3: complex job
print("=" * 60)
print("TEST 3: Complex headlight restoration")
print("=" * 60)
result = pricing_tool.invoke({"client_request": "My headlights are super foggy and yellowed, looks like a really tough restoration job"})
print(result)

# Test 4: premium service
print("=" * 60)
print("TEST 4: Ceramic coating quote")
print("=" * 60)
result = pricing_tool.invoke({"client_request": "I just got a new Tesla and want to protect the paint with a ceramic coating"})
print(result)