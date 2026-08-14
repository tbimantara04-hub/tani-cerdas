import sys
import os
import json
import unittest
from unittest.mock import MagicMock, patch

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock langchain / ollama / vectorstore libraries to prevent heavy loads
sys.modules['langchain_ollama'] = MagicMock()
sys.modules['langchain_community.vectorstores'] = MagicMock()
sys.modules['langchain_community.document_loaders'] = MagicMock()
sys.modules['langchain_text_splitters'] = MagicMock()

# Mock security to avoid Fernet decrypt errors on empty/unconfigured environments
import security
security.encryptor = MagicMock()
security.encryptor.encrypt.return_value = "encrypted_mock_data"
security.encryptor.decrypt.return_value = "[]"

# Mock chatbot & profile storage
import rag_logic
rag_logic.ask_chatbot = MagicMock(return_value=("Halo, ini jawaban bot.", []))
rag_logic.ambil_profil_petani = MagicMock(return_value={"tanaman": "padi", "luas_lahan": "2 hektar"})
rag_logic.simpan_profil_petani = MagicMock(return_value="Profil berhasil disimpan.")

from fastapi.testclient import TestClient
from main import app as legacy_app
from main_agentic import app as agentic_app

class TestAPIIntegrationLegacy(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(legacy_app)
        
    @patch("main.load_decrypted_data")
    @patch("main.save_encrypted_data")
    def test_legacy_chat_endpoint(self, mock_save, mock_load):
        mock_load.return_value = []
        response = self.client.post("/api/chat", json={"message": "Bagaimana cara menanam padi?", "llm_mode": "local"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("response", response.json())
        self.assertEqual(response.json()["response"], "Halo, ini jawaban bot.")
        
    @patch("main.load_decrypted_data")
    def test_legacy_history_endpoint(self, mock_load):
        mock_load.return_value = [{"user": "halo", "bot": "hai"}]
        response = self.client.get("/api/history")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["user"], "halo")

    @patch("main.load_decrypted_data")
    @patch("main.save_encrypted_data")
    def test_legacy_planting_endpoint(self, mock_save, mock_load):
        mock_load.return_value = []
        response = self.client.post("/api/planting", json={
            "plant_name": "Jagung",
            "notes": "Pupuk urea awal"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")

    def test_legacy_profile_endpoints(self):
        response = self.client.get("/api/profile")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["tanaman"], "padi")

        response = self.client.post("/api/profile", json={
            "tanaman": "jagung",
            "luas_lahan": "1 hektar"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")


class TestAPIIntegrationAgentic(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(agentic_app)

    @patch("main_agentic.get_orchestrator")
    @patch("main_agentic.load_decrypted_data")
    @patch("main_agentic.save_encrypted_data")
    def test_agentic_chat_endpoint(self, mock_save, mock_load, mock_orchestrator):
        mock_load.return_value = []
        
        # Mock orchestrator behavior
        mock_agent_orchestrator = MagicMock()
        mock_agent_orchestrator.process_query.return_value = {
            "response": "Ini respon agen cerdas.",
            "primary_agent": "advisory_agent"
        }
        mock_orchestrator.return_value = mock_agent_orchestrator

        response = self.client.post("/api/chat", json={"message": "padi kuning kena hama apa?", "llm_mode": "local"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["response"], "Ini respon agen cerdas.")

    @patch("main_agentic.load_decrypted_data")
    def test_agentic_history_endpoint(self, mock_load):
        mock_load.return_value = [{"user": "info cuaca", "bot": "cuaca cerah", "farmer_id": "default"}]
        response = self.client.get("/api/history")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["user"], "info cuaca")

if __name__ == "__main__":
    unittest.main()
