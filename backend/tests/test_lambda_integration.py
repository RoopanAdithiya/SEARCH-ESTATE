"""
tests/test_lambda_integration.py
--------------------------------
Automated integration tests verifying:
1. Dual-mode prediction provider (Local vs. Cloud Lambda toggle).
2. Numerical and explanation parity between local model and Lambda handler.
3. Graceful fallback behavior when cloud Lambda is unavailable.
"""

import sys
import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

_lambda_dir = _backend_dir.parent / "lambda"
if str(_lambda_dir) not in sys.path:
    sys.path.insert(0, str(_lambda_dir))

from main import app
from ml.services.prediction_service import analyze_property
from lambda_function import lambda_handler

client = TestClient(app)

PARITY_CASES = [
    {"locality": "Velachery", "sqft": 1000, "bhk": 2, "furnishing": "semi", "water_source": "metro", "age": 5},
    {"locality": "Anna Nagar", "sqft": 1400, "bhk": 3, "furnishing": "full", "water_source": "metro", "age": 2},
    {"locality": "Tambaram", "sqft": 700, "bhk": 1, "furnishing": "unfurnished", "water_source": "borewell", "age": 12},
    {"locality": "Nungambakkam", "sqft": 2000, "bhk": 4, "furnishing": "full", "water_source": "both", "age": 1},
    {"locality": "Chromepet", "sqft": 900, "bhk": 2, "furnishing": "semi", "water_source": "metro", "age": 8},
]


@pytest.mark.parametrize("case", PARITY_CASES)
def test_local_model_vs_lambda_handler_parity(case):
    """Verify local model and Lambda handler produce 100% identical predictions and explanations."""
    local_result = analyze_property(**case)
    lambda_result = lambda_handler(case, None)

    # Check predicted rent parity
    assert local_result["predicted_rent"] == lambda_result["predicted_rent"]
    assert local_result["status"] == "ok"
    assert lambda_result["status"] == "ok"

    # Check explanation parity
    local_expl = local_result["explanation"]
    lambda_expl = lambda_result["explanation"]
    assert len(local_expl) == len(lambda_expl) == 3

    for l_item, lam_item in zip(local_expl, lambda_expl):
        assert l_item["feature"] == lam_item["feature"]
        assert l_item["impact"] == lam_item["impact"]
        assert l_item["direction"] == lam_item["direction"]


def test_cloud_lambda_fallback_on_unreachable_endpoint(monkeypatch):
    """Verify application gracefully falls back to local inference when cloud endpoint is unavailable."""
    # Force cloud mode pointing to an unreachable endpoint
    monkeypatch.setenv("USE_CLOUD_LAMBDA", "true")
    monkeypatch.setenv("LAMBDA_ENDPOINT_URL", "http://127.0.0.1:9999/unreachable")
    monkeypatch.setenv("LAMBDA_TIMEOUT_SECONDS", "0.5")

    payload = {
        "locality": "Velachery",
        "sqft": 1000,
        "bhk": 2,
        "furnishing": "semi",
        "water_source": "metro",
        "age": 5,
    }

    # API should NOT crash; should succeed via local fallback
    response = client.post("/api/predict-rent", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["predicted_rent"] == 25000
