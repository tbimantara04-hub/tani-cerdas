import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock langchain libraries to prevent loading Ollama/FAISS during testing
sys.modules['langchain_ollama'] = MagicMock()
sys.modules['langchain_community.vectorstores'] = MagicMock()
sys.modules['langchain_community.document_loaders'] = MagicMock()
sys.modules['langchain_text_splitters'] = MagicMock()

# Mock security's encryptor so we don't depend on Fernet key validation during orchestrator/agent init
import security
security.encryptor = MagicMock()

from agents.weather_agent import WeatherAgent
from agents.price_agent import PriceAgent
from agents.knowledge_agent import KnowledgeAgent
from agents.advisory_agent import AdvisoryAgent

class TestAgents(unittest.TestCase):
    def test_weather_agent_tools(self):
        """Test tools list of WeatherAgent."""
        agent = WeatherAgent()
        tools = agent.get_available_tools()
        self.assertTrue(len(tools) > 0)
        self.assertEqual(tools[0]["name"], "cek_cuaca")

    def test_weather_agent_planning(self):
        """Test planning capability of WeatherAgent."""
        agent = WeatherAgent()
        query = "Bagaimana cuaca di Surabaya hari ini?"
        context = {"lokasi": "Surabaya"}
        plan = agent.plan(query, context)
        self.assertTrue(plan["needs_action"])
        self.assertEqual(plan["tool"], "cek_cuaca")
        self.assertEqual(plan["tool_params"]["lokasi"], "Surabaya")

    def test_weather_agent_alerts(self):
        """Test weather alerts detection."""
        agent = WeatherAgent()
        # Test extreme heat alert
        hot_weather = {
            "temperature": 38,
            "humidity": 60,
            "wind_speed": 10,
            "condition": "Cerah",
            "location": "Jakarta"
        }
        alerts = agent._check_weather_alerts(hot_weather)
        self.assertTrue(any("panas" in alert.lower() for alert in alerts))

        # Test extreme cold alert
        cold_weather = {
            "temperature": 8,
            "humidity": 60,
            "wind_speed": 10,
            "condition": "Dingin",
            "location": "Malang"
        }
        alerts = agent._check_weather_alerts(cold_weather)
        self.assertTrue(any("dingin" in alert.lower() for alert in alerts))

    def test_price_agent_tools(self):
        """Test tools list of PriceAgent."""
        agent = PriceAgent()
        tools = agent.get_available_tools()
        self.assertTrue(len(tools) > 0)
        self.assertEqual(tools[0]["name"], "cek_harga")

    def test_price_agent_planning(self):
        """Test planning capability of PriceAgent."""
        agent = PriceAgent()
        query = "Berapa harga cabai rawit hari ini?"
        context = {}
        plan = agent.plan(query, context)
        self.assertTrue(plan["needs_action"])
        self.assertEqual(plan["tool"], "cek_harga")
        self.assertEqual(plan["tool_params"]["komoditas"], "cabai")

    def test_price_agent_forecast(self):
        """Test price forecasting model output structure and heuristics."""
        agent = PriceAgent()
        forecast = agent.get_price_forecast("cabai", days_ahead=7)
        self.assertEqual(forecast["commodity"], "cabai")
        self.assertEqual(forecast["forecast_days"], 7)
        self.assertEqual(len(forecast["predictions"]), 7)
        self.assertEqual(forecast["model_type"], "seasonal_heuristic_v1")

    def test_knowledge_agent_tools(self):
        """Test tools list of KnowledgeAgent."""
        agent = KnowledgeAgent()
        tools = agent.get_available_tools()
        self.assertTrue(len(tools) > 0)
        self.assertEqual(tools[0]["name"], "tanya_panduan")

    def test_knowledge_agent_planning(self):
        """Test planning capability of KnowledgeAgent."""
        agent = KnowledgeAgent()
        query = "Bagaimana mengatasi hama wereng?"
        context = {}
        plan = agent.plan(query, context)
        self.assertTrue(plan["needs_action"])
        self.assertEqual(plan["tool"], "tanya_panduan")
        self.assertEqual(plan["expertise_area"], "pest_management")

    def test_advisory_agent_tools(self):
        """Test tools list of AdvisoryAgent."""
        agent = AdvisoryAgent()
        tools = agent.get_available_tools()
        self.assertEqual(len(tools), 2)
        self.assertTrue(any(t["name"] == "analyze_patterns" for t in tools))

if __name__ == "__main__":
    unittest.main()
