"""
ml/services/prediction_service.py
----------------------------------
The intelligent prediction layer between your API and the model provider.
Supports dual-mode execution:
  - Local in-process inference (default, offline development)
  - Cloud serverless inference via AWS Lambda (when USE_CLOUD_LAMBDA=True)
Includes automatic local fallback if the cloud Lambda invocation fails or times out.
Adds overpricing detection, rent stress ratio, and human-readable verdicts.
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Logger configuration
logger = logging.getLogger("prediction_service")

# ── Constants ─────────────────────────────────────────────────────────────────
OVERPRICING_THRESHOLD = 0.10   # 10% above predicted = overpriced
HIGH_STRESS_THRESHOLD = 0.40   # rent > 40% of income = high stress (standard rule)


def _get_cloud_config() -> dict:
    """Read cloud prediction configuration from environment variables."""
    use_cloud = os.getenv("USE_CLOUD_LAMBDA", "false").strip().lower() in ("true", "1", "yes")
    return {
        "use_cloud": use_cloud,
        "region": os.getenv("AWS_REGION", "ap-south-1"),
        "function_name": os.getenv("LAMBDA_FUNCTION_NAME", "search-estate-rent-predictor"),
        "endpoint_url": os.getenv("LAMBDA_ENDPOINT_URL", "").strip(),
        "timeout": float(os.getenv("LAMBDA_TIMEOUT_SECONDS", "5.0")),
    }


def _invoke_lambda(payload: dict, config: dict) -> Optional[dict]:
    """Invoke remote AWS Lambda function using boto3 or HTTP endpoint."""
    endpoint_url = config.get("endpoint_url")
    timeout = config.get("timeout", 5.0)

    # Path A: Function URL or HTTP Endpoint
    if endpoint_url:
        try:
            import httpx
            with httpx.Client(timeout=timeout) as client:
                resp = client.post(endpoint_url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    if isinstance(data, dict) and "body" in data and isinstance(data["body"], str):
                        data = json.loads(data["body"])
                    return data
                logger.warning(f"Lambda HTTP endpoint returned status {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.warning(f"Error calling Lambda HTTP endpoint: {e}")
        return None

    # Path B: AWS SDK (boto3) direct invocation
    try:
        import boto3
        from botocore.config import Config
        boto_cfg = Config(connect_timeout=2.0, read_timeout=timeout, retries={"max_attempts": 1})
        client = boto3.client("lambda", region_name=config["region"], config=boto_cfg)
        response = client.invoke(
            FunctionName=config["function_name"],
            InvocationType="RequestResponse",
            Payload=json.dumps(payload),
        )
        raw_payload = response["Payload"].read().decode("utf-8")
        parsed = json.loads(raw_payload)

        # Handle API Gateway style proxy response
        if isinstance(parsed, dict) and "body" in parsed and isinstance(parsed["body"], str):
            parsed = json.loads(parsed["body"])

        if isinstance(parsed, dict) and parsed.get("status") == "ok":
            return parsed
        logger.warning(f"Lambda invocation returned unexpected payload: {parsed}")
    except Exception as e:
        logger.warning(f"AWS Lambda boto3 invocation failed ({e}). Proceeding to local fallback.")

    return None


def analyze_property(
    locality: str,
    sqft: int,
    bhk: int,
    furnishing: str,
    water_source: str,
    age: int,
    listed_rent: int = None,
    monthly_income: int = None,
) -> dict:
    """
    Full property analysis — prediction + intelligence layer.
    Routes to AWS Lambda when USE_CLOUD_LAMBDA=True, with graceful local fallback.
    """
    cloud_cfg = _get_cloud_config()
    prediction = None
    provider_used = "local"

    payload = {
        "locality": locality,
        "sqft": sqft,
        "bhk": bhk,
        "furnishing": furnishing,
        "water_source": water_source,
        "age": age,
        "listed_rent": listed_rent,
        "monthly_income": monthly_income,
    }

    # Attempt Cloud Lambda if enabled
    if cloud_cfg["use_cloud"]:
        prediction = _invoke_lambda(payload, cloud_cfg)
        if prediction and prediction.get("status") == "ok":
            provider_used = "aws_lambda"
        else:
            logger.info("Falling back to local in-process model.")

    # Local in-process inference (default or fallback)
    if prediction is None or prediction.get("status") != "ok":
        from ml.predictor import predict_rent_with_shap
        prediction = predict_rent_with_shap(
            locality=locality,
            sqft=sqft,
            bhk=bhk,
            furnishing=furnishing,
            water_source=water_source,
            age=age,
        )
        if prediction.get("status") == "error":
            return prediction  # bubble up model error

    predicted_rent = prediction["predicted_rent"]
    result = {
        "predicted_rent": predicted_rent,
        "explanation":    prediction.get("explanation", []),
        "status":         "ok",
        "provider":       provider_used,
    }

    # ── Overpricing analysis ──────────────────────────────────────────────────
    if listed_rent is not None:
        difference     = listed_rent - predicted_rent
        diff_pct       = difference / predicted_rent

        is_overpriced  = diff_pct > OVERPRICING_THRESHOLD
        is_underpriced = diff_pct < -OVERPRICING_THRESHOLD

        if is_overpriced:
            overpricing_label = "overpriced"
        elif is_underpriced:
            overpricing_label = "good deal"
        else:
            overpricing_label = "fair price"

        result["overpricing"] = {
            "listed_rent":       listed_rent,
            "difference":        difference,
            "difference_pct":    round(diff_pct * 100, 1),
            "label":             overpricing_label,
            "is_overpriced":     is_overpriced,
        }

    # ── Rent stress ───────────────────────────────────────────────────────────
    if monthly_income is not None:
        rent_to_use   = listed_rent if listed_rent else predicted_rent
        stress_ratio  = rent_to_use / monthly_income

        if stress_ratio > HIGH_STRESS_THRESHOLD:
            stress_label = "high stress"
        elif stress_ratio > 0.25:
            stress_label = "moderate"
        else:
            stress_label = "comfortable"

        result["rent_stress"] = {
            "monthly_income":  monthly_income,
            "rent_to_income":  round(stress_ratio * 100, 1),
            "label":           stress_label,
            "is_high_stress":  stress_ratio > HIGH_STRESS_THRESHOLD,
        }

    # ── Human-readable verdict ───────────────────────────────────────────────
    verdict_parts = []

    if "overpricing" in result:
        op = result["overpricing"]
        if op["is_overpriced"]:
            verdict_parts.append(
                f"Listed ₹{listed_rent:,} is {op['difference_pct']}% above market — overpriced."
            )
        elif op["label"] == "good deal":
            verdict_parts.append(
                f"Listed ₹{listed_rent:,} is {abs(op['difference_pct'])}% below market — good deal."
            )
        else:
            verdict_parts.append("Listed rent is fairly priced.")

    if "rent_stress" in result:
        rs = result["rent_stress"]
        verdict_parts.append(
            f"Rent is {rs['rent_to_income']}% of income ({rs['label']})."
        )

    if not verdict_parts:
        verdict_parts.append(f"Predicted market rent for this property is ₹{predicted_rent:,}.")

    result["verdict"] = " ".join(verdict_parts)

    return result
