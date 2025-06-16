import re

def extract_entities(goal):
    # Example: extract multiple cities or books
    cities = re.findall(r"in ([A-Za-z ]+?)(?:,| and |$)", goal)
    books = re.findall(r"books? on ([A-Za-z ]+?)(?:,| and |$)", goal)
    if cities:
        return {"entities": [c.strip() for c in cities], "entity_key": "city"}
    if books:
        return {"entities": [b.strip() for b in books], "entity_key": "book"}
    # fallback: single city/topic
    city = None
    match = re.search(r"(?:in|for|at)\s+([A-Za-z ]+)", goal)
    if match:
        city = match.group(1).strip().split()[0]
    topic = None
    match = re.search(r"(?:books on|about|regarding)\s+([A-Za-z ]+)", goal)
    if match:
        topic = match.group(1).strip()
    return {"city": city, "topic": topic}