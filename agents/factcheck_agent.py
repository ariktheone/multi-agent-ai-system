import requests
import os

class FactCheckAgent:
    def run(self, context):
        claims = []
        if "news" in context:
            claims.extend(context["news"])
        checked = []
        api_key = os.getenv("GOOGLE_API_KEY")
        for claim in claims:
            # Google Fact Check API
            try:
                url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
                params = {"query": claim, "key": api_key}
                resp = requests.get(url, params=params, timeout=10)
                if resp.ok and resp.json().get("claims"):
                    verdict = resp.json()["claims"][0].get("text", "Verified")
                    checked.append({"claim": claim, "fact_check": verdict})
                else:
                    checked.append({"claim": claim, "fact_check": "No fact check found"})
            except Exception as e:
                checked.append({"claim": claim, "fact_check": f"Error: {e}"})
        # Consider validated if no claim is "False" or "Error"
        validated = all("False" not in c["fact_check"] and "Error" not in c["fact_check"] for c in checked)
        return {"fact_checks": checked, "validated": validated}