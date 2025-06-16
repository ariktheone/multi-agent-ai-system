import unittest
from main import execute_chain

class TestAgentChain(unittest.TestCase):
    def test_climate_goal(self):
        goal = "In-depth assessment of climate conditions in New York"
        chain = ["weather", "temperature", "air_quality", "summarizer"]
        result = execute_chain(chain, goal)
        self.assertIn("summary", result.data)
        self.assertGreater(len(result.data["summary"].split()), 30)

if __name__ == "__main__":
    unittest.main()