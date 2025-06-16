from textblob import TextBlob

class SentimentAgent:
    def run(self, context):
        news_batches = context.get("news", [])
        sentiments = []
        for batch in news_batches:
            text = " ".join(batch.get("news", []))
            if not text:
                sentiments.append({"entity": batch.get("entity"), "sentiment": "No text"})
                continue
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            if polarity > 0.1:
                sentiment = "Positive"
            elif polarity < -0.1:
                sentiment = "Negative"
            else:
                sentiment = "Neutral"
            sentiments.append({"entity": batch.get("entity"), "sentiment": sentiment})
        return {"sentiment": sentiments}