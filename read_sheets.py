from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SHEETS_SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SPREADSHEET_ID = "1wrItgWsgLmed3PlkaE8nuHEGBdgN20rXJAvDEvWWo1E"
RANGE_NAME = "PricingSheet!A1:G10"

def main():

    creds = Credentials.from_service_account_file(
        "service_account.json",
        scopes=SHEETS_SCOPES
    )

    service = build("sheets", "v4", credentials=creds)

    sheet = service.spreadsheets()

    result = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()

    values = result.get("values", [])

    if not values:
        print("No data found.")
        return

    print("\nSUCCESS: Spreadsheet data retrieved\n")

    for row in values:
        print(row)

if __name__ == "__main__":
    main()