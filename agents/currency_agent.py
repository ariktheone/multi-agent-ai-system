import requests

class CurrencyAgent:
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
                    return {"currency": f"1 {base} = {rate} {target}", "validated": True}
                else:
                    return {"currency": f"No rate found for {target}.", "validated": False}
            else:
                return {"currency": "No currency data found.", "validated": False}
        except Exception as e:
            return {"currency": f"Error fetching currency data: {e}", "validated": False}