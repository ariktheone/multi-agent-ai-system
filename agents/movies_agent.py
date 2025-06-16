import requests

class MoviesAgent:
    def run(self, context):
        # Example: Use OMDb API for movie info (free API key required, or demo fallback)
        movie = context.get("movie", "Inception")
        api_key = "demo"  # Replace with your OMDb API key if you have one
        url = f"http://www.omdbapi.com/?t={movie}&apikey={api_key}"
        try:
            resp = requests.get(url, timeout=10)
            if resp.ok:
                data = resp.json()
                if data.get("Response") == "True":
                    return {"movies": f"{data.get('Title')} ({data.get('Year')}): {data.get('Plot')}"}
                else:
                    return {"movies": f"No movie data found for '{movie}'."}
            else:
                return {"movies": "No movie data found."}
        except Exception as e:
            return {"movies": f"Error fetching movie data: {e}"}