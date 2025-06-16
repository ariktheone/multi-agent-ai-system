#summarizer_agent.py

import os
import requests
import logging
import textwrap
from transformers import pipeline

class SummarizerAgent:
    def __init__(self):
        self.bart_summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        self.cohere_api_key = os.getenv("COHERE_API_KEY", "")
        self.max_chunk_chars = 1600  # Increase chunk size for more context per summary

    # summarizer_agent.py (update format_context method)
    def format_context(self, context: dict) -> str:
        """Formats context into a detailed structured paragraph for N entities."""
        parts = []
        if context.get("goal"):
            parts.append(f"🔍 Goal:\n{context['goal']}\n")
        
        # Prefer formatted weather summary if available
        if context.get("weather_summary"):
            parts.append(f"🌤 Weather Summary:\n{context['weather_summary']}\n")
        
        # Handle batch results
        for key, value in context.items():
            # Skip raw weather dict if weather_summary is present
            if key in ("goal", "summary", "weather") and context.get("weather_summary"):
                continue
            if value:
                if isinstance(value, list) and value and isinstance(value[0], dict):
                    for item in value:
                        entity = item.get("entity") or item.get("topic") or ""
                        parts.append(f"🔹 {key.capitalize()} for {entity}:\n" +
                                     "\n".join(f"  - {k}: {v}" for k, v in item.items() if k != "entity"))
                elif isinstance(value, dict):
                    val_str = "\n".join(f"  • {k}: {v}" for k, v in value.items())
                    parts.append(f"🔹 {key.capitalize()}:\n{val_str}\n")
                elif isinstance(value, list):
                    val_str = "\n".join(f"  - {v}" for v in value)
                    parts.append(f"🔹 {key.capitalize()}:\n{val_str}\n")
                else:
                    parts.append(f"🔹 {key.capitalize()}:\n{str(value)}\n")
        return "\n".join(parts).strip() or "No relevant input found."

    # summarizer_agent.py (update cohere_in_depth_summary method)
    def cohere_in_depth_summary(self, text: str) -> str | None:
        """Uses Cohere for analytical summarization if API key is available."""
        try:
            response = requests.post(
                "https://api.cohere.ai/v1/summarize",
                headers={
                    "Authorization": f"Bearer {self.cohere_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "text": text,
                    "length": "auto",
                    "format": "paragraph",
                    "extractiveness": "low",  # Encourage analysis
                    "temperature": 0.7,
                    "additional_command": "Convert all temperature values from Kelvin to Fahrenheit and Celsius. Report temperatures in °F and °C"
                },
                timeout=15
            )
            if response.ok:
                result = response.json().get("summary")
                return result.strip() if result else None
        except Exception as e:
            logging.warning(f"[Cohere Error] {e}")
        return None

    def bart_deep_summary(self, text: str) -> str:
        """Fallback using BART with chunking and reflective summarization."""
        chunks = textwrap.wrap(text, width=self.max_chunk_chars)
        combined_summary = []

        for i, chunk in enumerate(chunks):
            try:
                # First summarization pass (raw summarization)
                basic_summary = self.bart_summarizer(
                    chunk,
                    max_length=350,   # Increase max length
                    min_length=120,   # Increase min length
                    do_sample=False
                )[0]['summary_text']

                # Second pass (reflective prompt)
                analysis_prompt = (
                    f"{basic_summary}\n\n"
                    f"Based on this, provide deeper insights, implications, or cause-effect relationships. "
                    f"Explain what this suggests or why it matters."
                )
                reflection = self.bart_summarizer(
                    analysis_prompt,
                    max_length=250,   # Increase max length
                    min_length=100,   # Increase min length
                    do_sample=False
                )[0]['summary_text']

                combined_summary.append(f"🧾 Section {i+1}:\n{reflection}")
            except Exception as e:
                logging.warning(f"[BART Summarization Error]: {e}")

        return "\n\n".join(combined_summary)

    def run(self, context: dict) -> str:
        input_text = self.format_context(context)

        # Prefer Cohere if available
        if self.cohere_api_key:
            summary = self.cohere_in_depth_summary(input_text)
            if summary and len(summary.split()) > 10:
                return f"📊 In-depth Analytical Summary (Cohere):\n{summary}"
            else:
                return "Summary: The available data was insufficient for a detailed summary, but key findings are presented below."

        # Fallback to in-depth BART pipeline
        summary = self.bart_deep_summary(input_text)
        if summary and len(summary.split()) > 10:
            return f"📊 In-depth Analytical Summary (Local BART):\n{summary}"
        else:
            return "Summary: The available data was insufficient for a detailed summary, but key findings are presented below."
