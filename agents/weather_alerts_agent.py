import requests
import os

class WeatherAlertsAgent:
    def run(self, context):
        city = context.get("city", "London")
        api_key = os.getenv("OPENWEATHERMAP_API_KEY")
        url = f"https://api.openweathermap.org/data/2.5/weather"
        params = {"q": city, "appid": api_key}
        try:
            resp = requests.get(url, params=params, timeout=10)
            if resp.ok:
                data = resp.json()
                alerts = data.get("alerts", [])
                if alerts:
                    return {"weather_alerts": [a.get("description", "Alert") for a in alerts]}
                else:
                    return {"weather_alerts": ["No weather alerts."]}
            else:
                return {"weather_alerts": ["No weather alert data found."]}
        except Exception as e:
            return {"weather_alerts": [f"Error fetching weather alerts: {e}"]}