import random
from datetime import datetime

class TrafficAgent:
    def run(self, context):
        # Support batch cities
        cities = context.get("entities") or [context.get("city", "Delhi")]
        results = []
        hour = datetime.now().hour
        for city in cities:
            # Simulate rush hour logic
            if 7 <= hour <= 10 or 17 <= hour <= 20:
                status = random.choices(
                    ["Heavy congestion", "Moderate traffic", "Light traffic", "No major incidents"],
                    weights=[0.5, 0.3, 0.15, 0.05]
                )[0]
                reasoning = "Rush hour: higher chance of congestion."
            else:
                status = random.choices(
                    ["Heavy congestion", "Moderate traffic", "Light traffic", "No major incidents"],
                    weights=[0.1, 0.3, 0.4, 0.2]
                )[0]
                reasoning = "Off-peak hours: less congestion likely."
            results.append({
                "city": city,
                "traffic": status,
                "validated": True,
                "reasoning": reasoning
            })
        return {"traffic": results}