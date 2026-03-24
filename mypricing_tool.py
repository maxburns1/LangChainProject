from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import json

SHEETS_SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SERVICE_ACCOUNT_FILE = "service_account.json"
SPREADSHEET_ID = "1wrItgWsgLmed3PlkaE8nuHEGBdgN20rXJAvDEvWWo1E"
RANGE_NAME = "PricingSheet!A1:G100"

def get_sheets_service():
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SHEETS_SCOPES
    )
    return build("sheets", "v4", credentials=creds)


@tool
def pricing_tool(client_request: str):
    """
    Review the customer's request and the business pricing sheet, then determine the best quote.
    Use this tool when the user asks for a quote, estimate, or pricing.
    """

    # Step 1: Read pricing data from Google Sheets
    sheets_service = get_sheets_service()
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME
    ).execute()

    rows = result.get("values", [])
    if not rows or len(rows) < 2:
        return "Pricing sheet is empty or unavailable."

    headers = rows[0]
    data_rows = rows[1:]

    pricing_records = []
    for row in data_rows:
        padded = row + [""] * (len(headers) - len(row))
        pricing_records.append(dict(zip(headers, padded)))

    # Step 2: Ask Gemini to interpret pricing
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0
    )

    prompt = f"""
You are a pricing analyst for a handyman business.

Your job is to review:
1. the customer request
2. the company's pricing structure

Then determine:
- the most likely service type
- the urgency level
- the complexity level
- the final estimated quote
- a brief explanation

Customer request:
{client_request}

Pricing data from Google Sheets:
{json.dumps(pricing_records, indent=2)}

Instructions:
- Use only the pricing data provided.
- Pick the best matching service from the pricing records.
- Infer urgency and complexity from the customer's wording if possible.
- urgency must be one of: normal, urgent, emergency
- complexity must be one of: simple, standard, complex
- estimated_price must be the final numeric price as a string with no dollar sign
- Show your reasoning briefly and clearly.
- If the request is ambiguous, choose the most reasonable option and say what assumption you made.
- Return only raw JSON.
- Do not use markdown code fences.
- Do not add any explanation before or after the JSON.
- The response must begin with {{ and end with }}.
- Use this exact format:
{{
  "service_type": "...",
  "urgency": "...",
  "complexity": "...",
  "estimated_price": "...",
  "explanation": "..."
}}

"""

    response = model.invoke(prompt)

    content = response.content
   # Convert to plain text
    if isinstance(content, str):
        text = content.strip()
    elif isinstance(content, list):
        text_parts = []
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                text_parts.append(part.get("text", ""))
            else:
                text_parts.append(str(part))
        text = "\n".join(text_parts).strip()
    else:
        text = str(content).strip()

    # Remove markdown code fences
    if text.startswith("```json"):
        text = text[len("```json"):].strip()

    if text.startswith("```"):
        text = text[len("```"):].strip()

    if text.endswith("```"):
        text = text[:-3].strip()

    pricing_result = json.loads(text)
    return json.dumps(pricing_result, indent=2)