"""
Tests for FastAPI API Endpoints with IDX80 Validation.
"""

import unittest
from fastapi.testclient import TestClient
from main import app


class TestAPIEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_root_endpoint(self):
        """GET / should return 200 and mention IDX80."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertIn("IDX80", data["message"])
        self.assertEqual(data.get("universe_count"), 80)

    def test_health_endpoint(self):
        """GET /health should return 200 and healthy status."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "ok")
        self.assertEqual(data.get("universe"), "IDX80")

    def test_universe_stats_endpoint(self):
        """GET /api/v1/universe/stats returns 80 total universe."""
        response = self.client.get("/api/v1/universe/stats")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("total_universe"), 80)
        self.assertIn("IDX80", data.get("display_label", ""))

    def test_root_api_universe_stats_endpoint(self):
        """GET /api/universe/stats (used by frontend ROOT_API) returns 80 total universe."""
        response = self.client.get("/api/universe/stats")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("total_universe"), 80)
        self.assertIn("IDX80", data.get("display_label", ""))


    def test_screener_progress_endpoint(self):
        """GET /api/v1/screener/progress returns progress object."""
        response = self.client.get("/api/v1/screener/progress")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("is_running", data)
        self.assertIn("percent", data)

    def test_stock_historical_non_idx80_rejected(self):
        """GET /api/v1/stock/INVALID returns 400 Bad Request."""
        response = self.client.get("/api/v1/stock/INVALID_STOCK")
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("detail", data)
        self.assertIn("IDX80", data["detail"])

    def test_analysis_non_idx80_rejected(self):
        """GET /api/v1/analysis/INVALID returns 400 Bad Request."""
        response = self.client.get("/api/v1/analysis/NON_IDX80")
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("detail", data)
        self.assertIn("IDX80", data["detail"])

    def test_indicators_non_idx80_rejected(self):
        """GET /api/v1/indicators/INVALID returns 400 Bad Request."""
        response = self.client.get("/api/v1/indicators/NOT_IN_INDEX")
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("detail", data)
        self.assertIn("IDX80", data["detail"])


if __name__ == "__main__":
    unittest.main()
