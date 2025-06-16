import requests

class ExchangeRateAgent:
    def run(self, context):
        base = context.get("base_currency", "USD")
        target = context.get("target_currency", "INR")
        url = f"https://api.exchangerate-api.com/v4/latest/{base}"
        try:
            resp = requests.get(url, timeout=10)
            if resp.ok:
                data = resp.json()
                rate = data["rates"].get(target)
                if rate:
                    return {"exchange_rate": f"1 {base} = {rate} {target}"}
                else:
                    return {"exchange_rate": f"No rate found for {target}."}
            else:
                return {"exchange_rate": "No exchange rate data found."}
        except Exception as e:
            return {"exchange_rate": f"Error fetching exchange rate: {e}"}