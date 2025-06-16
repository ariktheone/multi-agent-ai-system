import requests
from datetime import datetime

class HolidaysAgent:
    def run(self, context):
        # Try to get country code from weather/sys or context
        country = None
        if "weather" in context and isinstance(context["weather"], dict):
            sys = context["weather"].get("sys", {})
            country = sys.get("country")
        if not country:
            country = context.get("country", "IN")
        year = str(datetime.now().year)
        url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/{country}"
        try:
            resp = requests.get(url, timeout=10)
            if resp.ok and resp.headers.get("Content-Type", "").startswith("application/json"):
                holidays = [h["localName"] for h in resp.json()]
                return {"holidays": holidays[:3] if holidays else ["No holidays found."]}
            else:
                return {"holidays": ["No holiday data found (bad response)."]}
        except Exception as e:
            return {"holidays": [f"Error fetching holidays: {e}"]}