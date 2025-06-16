import requests
import os

class HealthAgent:
    def run(self, context):
        # Example: Use news API for health news, or WHO API for stats if available
        topic = context.get("topic", "public health")
        city = context.get("city")
        query = f"{topic} {city}" if city else topic
        api_key = os.getenv("NEWSDATA_API_KEY", "")
        url = "https://newsdata.io/api/1/news"
        params = {"apikey": api_key, "q": query, "language": "en", "category": "health"}
        try:
            resp = requests.get(url, params=params, timeout=10)
            if resp.ok:
                articles = resp.json().get("results", [])
                news = [a["title"] for a in articles[:3]] if articles else ["No health news found."]
                return {"health": news, "validated": bool(articles)}
            else:
                return {"health": ["No health data found."], "validated": False}
        except Exception as e:
            return {"health": [f"Error fetching health data: {e}"], "validated": False}