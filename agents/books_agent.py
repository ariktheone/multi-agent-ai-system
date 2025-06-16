import requests

class BooksAgent:
    def run(self, context):
        # Support batch topics
        topics = context.get("entities") or [context.get("topic") or "artificial intelligence"]
        all_books = []
        for topic in topics:
            url = f"https://www.googleapis.com/books/v1/volumes"
            params = {"q": topic, "maxResults": 3}
            resp = requests.get(url, params=params)
            books = []
            if resp.ok:
                items = resp.json().get("items", [])
                for item in items:
                    info = item.get("volumeInfo", {})
                    title = info.get("title", "Unknown")
                    authors = ", ".join(info.get("authors", []))
                    desc = info.get("description", "")[:200]
                    books.append({"title": title, "authors": authors, "desc": desc})
            all_books.append({"topic": topic, "books": books})
        return {"books": all_books}