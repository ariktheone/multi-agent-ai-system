import random

class JobMarketAgent:
    def run(self, context):
        sector = context.get("sector", "technology")
        city = context.get("city", "Bangalore")
        # Demo: randomly generate job trend
        trend = random.choice(["Growing", "Stable", "Declining"])
        return {"job_market": f"Job market for {sector} in {city}: {trend}", "validated": True}