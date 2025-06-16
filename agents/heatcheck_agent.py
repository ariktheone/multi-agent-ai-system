import requests
import os

class HeatCheckAgent:
    def run(self, context):
        city = context.get("city", "Delhi")
        api_key = os.getenv("OPENWEATHERMAP_API_KEY")
        url = f"https://api.openweathermap.org/data/2.5/weather"
        params = {"q": city, "appid": api_key, "units": "metric"}
        try:
            resp = requests.get(url, params=params, timeout=10)
            if resp.ok:
                data = resp.json()
                temp = data.get("main", {}).get("temp")
                alerts = []
                if temp and temp > 40:
                    alerts.append(f"Heatwave alert: Current temperature in {city} is {temp}°C.")
                else:
                    alerts.append(f"Current temperature in {city} is {temp}°C.")
                return {"heatcheck": alerts, "validated": True}
            else:
                return {"heatcheck": ["No temperature data found."], "validated": False}
        except Exception as e:
            return {"heatcheck": [f"Error fetching temperature data: {e}"], "validated": False}