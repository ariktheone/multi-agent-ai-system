import requests, os

class FinanceAgent:
    def run(self, context):
        symbols = context.get("entities") or [context.get("symbol") or "AAPL"]
        api_key = os.getenv("ALPHA_VANTAGE_KEY")
        url = f"https://www.alphavantage.co/query"
        results = []
        for symbol in symbols:
            params = {"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": api_key}
            try:
                resp = requests.get(url, params=params, timeout=10)
                if resp.ok and "Global Quote" in resp.json():
                    quote = resp.json()["Global Quote"]
                    price = quote.get('05. price', 'N/A')
                    results.append({
                        "symbol": symbol,
                        "price": price,
                        "validated": price != 'N/A',
                        "reasoning": f"Fetched price for {symbol}."
                    })
                else:
                    results.append({
                        "symbol": symbol,
                        "price": "No data",
                        "validated": False,
                        "reasoning": "No quote found."
                    })
            except Exception as e:
                results.append({
                    "symbol": symbol,
                    "price": f"Error: {e}",
                    "validated": False,
                    "reasoning": f"Exception: {e}"
                })
        return {"finance": results}