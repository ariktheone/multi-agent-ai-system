import requests
import os

class PollutionAgent:
    def run(self, context):
        city = context.get("city", "Delhi")
        api_key = os.getenv("OPENWEATHERMAP_API_KEY")
        lat = context.get("lat")
        lon = context.get("lon")
        reasoning = []

        # Try to use lat/lon from context, else geocode
        if not (lat and lon):
            geo_url = f"http://api.openweathermap.org/geo/1.0/direct"
            geo_params = {"q": city, "limit": 1, "appid": api_key}
            geo_resp = requests.get(geo_url, params=geo_params)
            if geo_resp.ok and geo_resp.json():
                lat = geo_resp.json()[0]["lat"]
                lon = geo_resp.json()[0]["lon"]
                reasoning.append("Used OpenWeatherMap geocoding for lat/lon.")
            else:
                reasoning.append("Failed to geocode city.")
        if not (lat and lon):
            return {"pollution": "No location data found.", "validated": False, "reasoning": reasoning}

        params = {"lat": lat, "lon": lon, "appid": api_key}
        try:
            resp = requests.get("http://api.openweathermap.org/data/2.5/air_pollution", params=params, timeout=10)
            if resp.ok:
                data = resp.json()
                aqi = data.get("list", [{}])[0].get("main", {}).get("aqi")
                reasoning.append(f"Fetched AQI for {city}: {aqi}")
                return {"pollution": f"Air Quality Index (AQI) in {city}: {aqi}", "validated": True, "reasoning": reasoning}
            else:
                reasoning.append("Primary API failed, no pollution data found.")
                return {"pollution": "No pollution data found.", "validated": False, "reasoning": reasoning}
        except Exception as e:
            reasoning.append(f"Error fetching pollution data: {e}")
            return {"pollution": f"Error fetching pollution data: {e}", "validated": False, "reasoning": reasoning}