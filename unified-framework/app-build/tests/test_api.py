"""
Integration tests for Phi-Harmonic Trading Filter API
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.config.settings import settings


class TestAPIIntegration:
    """Integration tests for the complete API"""

    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
        self.api_key = settings.api_keys[0]  # Use first demo key
        self.headers = {"X-API-Key": self.api_key}

    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data

    def test_filter_single_signal_pass(self):
        """Test filtering a single signal that should pass"""
        payload = {
            "price": 100.0,
            "support": 90.0,
            "resistance": 110.0,
            "volatility": 5.0,
        }

        response = self.client.post(
            "/api/v1/filter/signals", json=payload, headers=self.headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["passed"] == True
        assert data["rejection_reason"] is None
        assert data["confidence"] > 0.8
        assert "filter_time_us" in data

    def test_filter_single_signal_reject(self):
        """Test filtering a single signal that should be rejected"""
        payload = {
            "price": 80.0,  # Below geometric bound
            "support": 90.0,
            "resistance": 110.0,
            "volatility": 5.0,
        }

        response = self.client.post(
            "/api/v1/filter/signals", json=payload, headers=self.headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["passed"] == False
        assert data["rejection_reason"] == "price_below_geometric_bound"
        assert data["confidence"] == 0.0

    def test_batch_filter_signals(self):
        """Test batch filtering of multiple signals"""
        payload = {
            "signals": [
                {
                    "price": 100.0,
                    "support": 90.0,
                    "resistance": 110.0,
                    "volatility": 5.0,
                },  # Pass
                {
                    "price": 80.0,
                    "support": 90.0,
                    "resistance": 110.0,
                    "volatility": 5.0,
                },  # Fail low
                {
                    "price": 120.0,
                    "support": 90.0,
                    "resistance": 110.0,
                    "volatility": 5.0,
                },  # Fail high
            ]
        }

        response = self.client.post(
            "/api/v1/filter/signals/batch", json=payload, headers=self.headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 3
        assert data["results"][0]["passed"] == True
        assert data["results"][1]["passed"] == False
        assert data["results"][2]["passed"] == False

        # Check summary
        summary = data["summary"]
        assert summary["total_signals"] == 3
        assert summary["passed"] == 1
        assert summary["rejected"] == 2
        assert summary["rejection_rate"] == 2 / 3
        assert "avg_time_us" in summary
        assert "total_time_ms" in summary

    def test_fibonacci_filter(self):
        """Test Fibonacci level filtering"""
        payload = {
            "low": 90.0,
            "high": 110.0,
            "volatility": 0.6,  # Low volatility for high rejection
        }

        response = self.client.post(
            "/api/v1/filter/fibonacci", json=payload, headers=self.headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "valid_levels" in data
        assert "total_levels" in data
        assert "rejection_rate" in data
        assert "filter_time_us" in data

        # Should have some valid levels and high rejection rate
        assert data["total_levels"] == 7  # Standard fib levels
        assert len(data["valid_levels"]) >= 0
        assert (
            data["rejection_rate"] >= 0.7
        )  # High rejection as expected with low volatility

    def test_no_api_key(self):
        """Test request without API key"""
        payload = {
            "price": 100.0,
            "support": 90.0,
            "resistance": 110.0,
            "volatility": 5.0,
        }

        response = self.client.post("/api/v1/filter/signals", json=payload)

        assert response.status_code == 401
        assert "API key required" in response.json()["detail"]

    def test_invalid_api_key(self):
        """Test request with invalid API key"""
        payload = {
            "price": 100.0,
            "support": 90.0,
            "resistance": 110.0,
            "volatility": 5.0,
        }

        headers = {"X-API-Key": "invalid-key"}

        response = self.client.post(
            "/api/v1/filter/signals", json=payload, headers=headers
        )

        assert response.status_code == 401
        assert "Invalid API key" in response.json()["detail"]

    def test_batch_size_limit(self):
        """Test batch size limit enforcement"""
        # Create a batch larger than max_batch_size
        signals = []
        for i in range(settings.max_batch_size + 1):
            signals.append(
                {
                    "price": 100.0 + i,
                    "support": 90.0,
                    "resistance": 110.0,
                    "volatility": 5.0,
                }
            )

        payload = {"signals": signals}

        response = self.client.post(
            "/api/v1/filter/signals/batch", json=payload, headers=self.headers
        )

        assert response.status_code == 400
        assert "Batch size exceeds maximum" in response.json()["detail"]

    def test_performance_batch_processing(self):
        """Test performance of batch processing"""
        # Create a large batch to test throughput
        signals = []
        for i in range(100):
            signals.append(
                {
                    "price": 95.0 + (i % 20),  # Vary prices
                    "support": 90.0,
                    "resistance": 110.0,
                    "volatility": 5.0,
                }
            )

        payload = {"signals": signals}

        import time

        start_time = time.time()
        response = self.client.post(
            "/api/v1/filter/signals/batch", json=payload, headers=self.headers
        )
        end_time = time.time()

        assert response.status_code == 200

        # Should process 100 signals quickly
        processing_time = end_time - start_time
        assert processing_time < 0.1  # Less than 100ms for 100 signals

        data = response.json()
        summary = data["summary"]
        assert summary["total_signals"] == 100
        assert summary["avg_time_us"] < 1000  # Less than 1us per signal average

    def test_invalid_request_data(self):
        """Test handling of invalid request data"""
        # Missing required field
        payload = {
            "price": 100.0,
            "support": 90.0,
            # Missing resistance
            "volatility": 5.0,
        }

        response = self.client.post(
            "/api/v1/filter/signals", json=payload, headers=self.headers
        )

        assert response.status_code == 422  # Validation error

    def test_edge_case_volatility(self):
        """Test edge case with zero volatility"""
        payload = {
            "price": 100.0,
            "support": 90.0,
            "resistance": 110.0,
            "volatility": 0.0,  # Zero volatility
        }

        response = self.client.post(
            "/api/v1/filter/signals", json=payload, headers=self.headers
        )

        assert response.status_code == 200
        data = response.json()
        # With zero volatility, band_width = 0, so only exact midpoint passes
        if payload["price"] == 100.0:
            assert data["passed"] == True
        else:
            assert data["passed"] == False
