import requests, os

class NewsAgent:
    def __init__(self):
        self.endpoint = "https://newsdata.io/api/1/news"
        self.api_key = os.getenv("NEWSDATA_API_KEY", "")

    def run(self, context):
        entities = context.get("entities")
        results = []
        queries = entities if entities else [context.get("location") or context.get("city") or context.get("topic")]
        if not queries or queries == [None]:
            if context.get("goal"):
                import re
                match = re.search(r"in ([A-Za-z ,]+)", context["goal"])
                if match:
                    queries = [match.group(1).strip().split(",")[0]]
                else:
                    queries = [" ".join(context["goal"].split()[:2])]
        for query in queries:
            if not query:
                continue
            params = {
                "apikey": self.api_key,
                "q": query,
                "language": "en"
            }
            try:
                resp = requests.get(self.endpoint, params=params, timeout=10)
                resp.raise_for_status()
                articles = resp.json().get("results", [])
                if articles:
                    results.append({
                        "entity": query,
                        "news": [a["title"] for a in articles[:3]],
                        "validated": True,
                        "reasoning": f"Fetched {len(articles)} articles for {query}."
                    })
                else:
                    results.append({
                        "entity": query,
                        "news": ["No news found for this topic."],
                        "validated": False,
                        "reasoning": "No articles found."
                    })
            except Exception as e:
                results.append({
                    "entity": query,
                    "news": [f"Error: {e}"],
                    "validated": False,
                    "reasoning": f"Exception: {e}"
                })
        return {"news": results}