import requests

class SportsAgent:
    def run(self, context):
        # Example: Use TheSportsDB API for sports news (free API key required)
        sport = context.get("sport", "Soccer")
        url = f"https://www.thesportsdb.com/api/v1/json/1/search_all_leagues.php?s={sport}"
        try:
            resp = requests.get(url, timeout=10)
            if resp.ok:
                data = resp.json()
                leagues = data.get("countrys", [])
                if leagues:
                    return {"sports": [l.get("strLeague") for l in leagues[:3]]}
                else:
                    return {"sports": ["No sports data found."]}
            else:
                return {"sports": ["No sports data found."]}
        except Exception as e:
            return {"sports": [f"Error fetching sports data: {e}"]}