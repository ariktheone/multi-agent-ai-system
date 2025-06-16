import requests

class WikipediaAgent:
    def run(self, context):
        # Use city, location, or a keyword from the goal
        query = context.get("location") or context.get("city")
        if not query and context.get("goal"):
            import re
            match = re.search(r"for ([A-Za-z ]+)", context["goal"])
            if match:
                query = match.group(1).strip()
        if not query:
            return {"wikipedia": "No relevant topic found."}
        resp = requests.get(
            "https://en.wikipedia.org/api/rest_v1/page/summary/" + query.replace(" ", "_")
        )
        if resp.ok:
            data = resp.json()
            return {"wikipedia": data.get("extract", "No summary found.")}
        return {"wikipedia": "No Wikipedia data found."}