import requests
from datetime import datetime

class EventAgent:
    def run(self, context):
        country = context.get("country", "IN")
        year = str(datetime.now().year)
        url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/{country}"
        try:
            resp = requests.get(url, timeout=10)
            if resp.ok:
                holidays = [h["localName"] for h in resp.json()][:3]
                return {"events": holidays, "validated": True}
            else:
                return {"events": ["No event data found."], "validated": False}
        except Exception as e:
            return {"events": [f"Error fetching events: {e}"], "validated": False}