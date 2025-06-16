import requests, os
from utils.api_limiter import rate_limited

class DataFetcherAgent:
    def __init__(self, config):
        self.endpoint = config["endpoint"]
        self.method = config["method"]
        self.api_key = os.getenv(config.get("key_env_var"), "")
        self.rate_limit = config["rate_limit"]

    @rate_limited(calls_per_period=60, period_seconds=60)
    def run(self, params=None):
        headers = {"Authorization": self.api_key} if self.api_key else {}
        resp = requests.request(self.method, self.endpoint, headers=headers, params=params)
        resp.raise_for_status()
        return resp.json()