# Gleam Mobile Detailing — AI Booking Agent

A LangChain agent that handles quote estimates, schedule lookups, and appointment 
booking for a mobile car detailing business. Powered by Gemini 2.5 Flash, Google 
Sheets (pricing data), and Google Calendar (scheduling).

## Setup
1. `python -m venv .venv` and activate it
2. `pip install -r requirements.txt`
3. Create a `.env` file with `GEMINI_API_KEY=your_key_here`
4. Add your own `service_account.json` (Google Sheets API)
5. Add your own `credentials.json` (Google Calendar OAuth desktop)
6. Update the `SPREADSHEET_ID` in `mypricing_tool.py` to point at your own pricing sheet

## Usage
- Test individual tools: `python test_pricing.py`, `python test_scheduling.py`, `python test_booking.py`
- Run the agent: `python main.py`

## Notes
Customized from a starter project for a mobile car detailing business. 
Services priced via Google Sheet; bookings written to Google Calendar.
