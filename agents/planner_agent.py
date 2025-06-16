import google.generativeai as genai
import os
import ast
import re

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class PlannerAgent:
    def plan(self, goal, available_agents):
        prompt = f"""
        You are an AI planner for a multi-agent system.
        User goal: '{goal}'.
        Available agents: {available_agents}.
        Provide the optimal ordered agent chain as a Python list (e.g. ['spacex_next','weather','summarizer']).
        Only output the list, nothing else.
        Always place 'summarizer' as the last agent in the chain, so it can summarize all enriched context.
        """
        model = genai.GenerativeModel("models/gemini-2.0-flash-lite")
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Remove Markdown code block if present
        if text.startswith("```"):
            text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
            text = text.split("```")[0].strip()
        # Try to find a Python list in the response
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("[") and line.endswith("]"):
                try:
                    return ast.literal_eval(line)
                except Exception:
                    continue
            match = re.match(r"^\w+\s*=\s*(\[.*\])$", line)
            if match:
                try:
                    return ast.literal_eval(match.group(1))
                except Exception:
                    continue
        match = re.search(r"(\[.*\])", text, re.DOTALL)
        if match:
            try:
                return ast.literal_eval(match.group(1))
            except Exception:
                pass
        try:
            return ast.literal_eval(text)
        except Exception as e:
            raise ValueError(f"Could not parse agent chain from model response: {text}") from e