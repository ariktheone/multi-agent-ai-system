import requests

class WikipediaSummaryAgent:
    def run(self, context):
        topic = context.get("topic") or context.get("goal")
        if not topic:
            return {"wikipedia_summary": "No topic provided."}
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic.replace(' ', '_')}"
        try:
            resp = requests.get(url, timeout=10)
            if resp.ok:
                data = resp.json()
                return {"wikipedia_summary": data.get("extract", "No summary found.")}
            else:
                return {"wikipedia_summary": "No Wikipedia summary found."}
        except Exception as e:
            return {"wikipedia_summary": f"Error fetching Wikipedia summary: {e}"}