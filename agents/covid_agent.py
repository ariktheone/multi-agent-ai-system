import requests

class COVIDAgent:
    def run(self, context):
        # Example: Use disease.sh API for COVID stats
        country = context.get("country", "India")
        url = f"https://disease.sh/v3/covid-19/countries/{country}"
        try:
            resp = requests.get(url, timeout=10)
            if resp.ok:
                data = resp.json()
                return {
                    "covid": f"Cases: {data.get('cases')}, Deaths: {data.get('deaths')}, Recovered: {data.get('recovered')}"
                }
            else:
                return {"covid": "No COVID data found."}
        except Exception as e:
            return {"covid": f"Error fetching COVID data: {e}"}