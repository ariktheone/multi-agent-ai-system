import os
import requests
from dotenv import load_dotenv
load_dotenv()

class APIFetchAgent:
    def __init__(self, config):
        self.config = config

    def run(self, context):
        if self.config.get("name") == "weather":
            # Try to extract a valid city name from entities
            city = None
            # Example: pick the first entity that looks like a city (improve this as needed)
            if "entities" in context and context["entities"]:
                # Try to extract just the city name (first two words)
                city_candidate = context["entities"][0]
                city = " ".join(city_candidate.split()[:2])
            elif "city" in context:
                city = context["city"]
            else:
                city = "New York"  # fallback

            api_key = os.getenv(self.config.get("api_key_env", "OPENWEATHER_KEY"))
            url = self.config.get("endpoint")
            params = {"q": city, "appid": api_key}
            resp = requests.get(url, params=params)
            resp.raise_for_status()
            return resp.json()
        # ... handle other agents as before ...