"""
lambda/test_lambda_local.py
--------------------------
Unit and parity testing harness for AWS Lambda inference handler.
Verifies input validation, cold/warm execution time, response schemas,
and 100% numerical parity against ground-truth model outputs.
"""

import sys
import json
import time
from pathlib import Path

# Add lambda directory to sys.path
_lambda_dir = Path(__file__).resolve().parent
if str(_lambda_dir) not in sys.path:
    sys.path.insert(0, str(_lambda_dir))

from lambda_function import lambda_handler

BASELINE_CASES = [
    {
        "name": "Velachery 2BHK",
        "input": {"locality": "Velachery", "sqft": 1000, "bhk": 2, "furnishing": "semi", "water_source": "metro", "age": 5},
        "expected_rent": 25000,
    },
    {
        "name": "Anna Nagar 3BHK",
        "input": {"locality": "Anna Nagar", "sqft": 1400, "bhk": 3, "furnishing": "full", "water_source": "metro", "age": 2},
        "expected_rent": 43500,
    },
    {
        "name": "Tambaram 1BHK",
        "input": {"locality": "Tambaram", "sqft": 700, "bhk": 1, "furnishing": "unfurnished", "water_source": "borewell", "age": 12},
        "expected_rent": 13000,
    },
    {
        "name": "Nungambakkam 4BHK",
        "input": {"locality": "Nungambakkam", "sqft": 2000, "bhk": 4, "furnishing": "full", "water_source": "both", "age": 1},
        "expected_rent": 57000,
    },
    {
        "name": "Chromepet 2BHK",
        "input": {"locality": "Chromepet", "sqft": 900, "bhk": 2, "furnishing": "semi", "water_source": "metro", "age": 8},
        "expected_rent": 18000,
    },
]


def test_lambda_handler_parity():
    """Verify all 5 baseline cases achieve exact parity in Lambda handler."""
    print("=" * 65)
    print("🧪  Testing Lambda Handler: Numerical Parity with Trained Model")
    print("=" * 65)

    for case in BASELINE_CASES:
        t0 = time.perf_counter()
        response = lambda_handler(case["input"], None)
        duration_ms = (time.perf_counter() - t0) * 1000

        assert response["statusCode"] == 200, f"Expected 200, got {response['statusCode']}"
        assert response["predicted_rent"] == case["expected_rent"], (
            f"Parity mismatch for {case['name']}: expected {case['expected_rent']}, got {response['predicted_rent']}"
        )
        assert len(response["explanation"]) == 3, "Expected 3 SHAP feature explanations"

        print(f"  ✅ {case['name']:<18} → Predicted: ₹{response['predicted_rent']:,} ({duration_ms:.2f} ms)")
        for feat in response["explanation"]:
            print(f"       • {feat['feature']:<22} : {feat['impact']:+6d} ({feat['direction']})")


def test_lambda_http_proxy_event():
    """Verify Lambda handler correctly decodes API Gateway / Function URL event with JSON body string."""
    print("\n🧪  Testing Lambda Handler: HTTP Proxy Event (API Gateway / Function URL)")
    http_event = {
        "rawPath": "/predict-rent",
        "headers": {"content-type": "application/json"},
        "body": json.dumps({
            "locality": "Velachery",
            "sqft": 1000,
            "bhk": 2,
            "furnishing": "semi",
            "water_source": "metro",
            "age": 5,
            "listed_rent": 30000,
            "monthly_income": 60000,
        })
    }
    response = lambda_handler(http_event, None)
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["predicted_rent"] == 25000
    assert body["overpricing"]["is_overpriced"] is True
    assert body["overpricing"]["difference_pct"] == 20.0
    assert body["rent_stress"]["is_high_stress"] is True
    assert body["rent_stress"]["rent_to_income"] == 50.0
    print("  ✅ HTTP proxy parsing and intelligence layers verified successfully.")


def test_lambda_input_validation():
    """Verify input validation returns 422 with clear error diagnostics."""
    print("\n🧪  Testing Lambda Handler: Input Validation & Error Handling")

    invalid_cases = [
        ({"locality": "Bangalore", "sqft": 1000, "bhk": 2, "furnishing": "semi", "water_source": "metro", "age": 5}, "Invalid locality"),
        ({"locality": "Velachery", "sqft": 50, "bhk": 2, "furnishing": "semi", "water_source": "metro", "age": 5}, "sqft must be between 100 and 10000"),
        ({"locality": "Velachery", "sqft": 1000, "bhk": 5, "furnishing": "semi", "water_source": "metro", "age": 5}, "bhk must be 1, 2, 3, or 4"),
        ({"locality": "Velachery", "sqft": 1000, "bhk": 2, "furnishing": "ultra_deluxe", "water_source": "metro", "age": 5}, "furnishing must be one of"),
    ]

    for payload, expected_err in invalid_cases:
        response = lambda_handler(payload, None)
        assert response["statusCode"] == 422, f"Expected 422, got {response['statusCode']}"
        body = json.loads(response["body"]) if isinstance(response["body"], str) else response["body"]
        assert any(expected_err.lower() in err.lower() for err in body["errors"]), f"Expected '{expected_err}' in errors"
        print(f"  ✅ Caught invalid input: {expected_err}")


def test_lambda_malformed_json():
    """Verify malformed JSON body returns 400."""
    print("\n🧪  Testing Lambda Handler: Malformed JSON")
    malformed_event = {"body": "{locality: 'Velachery' unclosed json"}
    response = lambda_handler(malformed_event, None)
    assert response["statusCode"] == 400
    print("  ✅ Caught malformed JSON body with HTTP 400.")


if __name__ == "__main__":
    test_lambda_handler_parity()
    test_lambda_http_proxy_event()
    test_lambda_input_validation()
    test_lambda_malformed_json()
    print("\n🎉 All Lambda handler unit tests passed successfully!")
