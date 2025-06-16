# agents/air_quality_agent.py
import requests
import os

class AirQualityAgent:
    def run(self, context):
        token = os.getenv("AQICN_TOKEN", "")
        city = context.get("location") or context.get("city") or "Kolkata"
        url = f"https://api.waqi.info/feed/{city}/?token={token}"
        resp = requests.get(url)
        if resp.ok and resp.json().get("status") == "ok":
            data = resp.json()["data"]
            return {"air_quality": f"AQI: {data['aqi']}, Dominant Pollutant: {data.get('dominentpol', 'N/A')}"}
        return {"air_quality": "No air quality data found."}