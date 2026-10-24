"""
lambda_function.py
------------------
AWS Lambda handler for Serverless Fair Rent Prediction with Tree SHAP explainability.
Designed for high performance, minimal memory footprint, and low cold-start latency.
Reuses the exact trained XGBoost model and calculates exact Tree SHAP values via
XGBoost's native pred_contribs algorithm (eliminating heavy external dependencies).
"""

import os
import json
import pickle
import numpy as np
import xgboost as xgb

# ── 1. Warm Initialization (Executed once per Lambda container cold start) ───
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_MODEL_PATH = os.path.join(_CURRENT_DIR, "models", "rent_model.pkl")
_COLS_PATH = os.path.join(_CURRENT_DIR, "models", "feature_columns.pkl")

# Locality coordinates and valid validation sets
VALID_LOCALITIES = [
    "Velachery", "Anna Nagar", "Adyar", "T Nagar", "Porur",
    "Chromepet", "Sholinganallur", "Perambur", "Korattur", "Medavakkam",
    "Tambaram", "Mylapore", "Nungambakkam", "Kodambakkam", "OMR"
]
VALID_FURNISHING = ["full", "semi", "unfurnished"]
VALID_WATER_SOURCE = ["metro", "borewell", "both"]

# Human-readable feature name mapping
FEATURE_LABELS = {
    "sqft": "Property Size",
    "bhk": "No. of Bedrooms",
    "age": "Building Age",
    "locality_Velachery": "Location (Velachery)",
    "locality_Anna Nagar": "Location (Anna Nagar)",
    "locality_Adyar": "Location (Adyar)",
    "locality_T Nagar": "Location (T Nagar)",
    "locality_Porur": "Location (Porur)",
    "locality_Chromepet": "Location (Chromepet)",
    "locality_Sholinganallur": "Location (Sholinganallur)",
    "locality_Perambur": "Location (Perambur)",
    "locality_Korattur": "Location (Korattur)",
    "locality_Medavakkam": "Location (Medavakkam)",
    "locality_Tambaram": "Location (Tambaram)",
    "locality_Mylapore": "Location (Mylapore)",
    "locality_Nungambakkam": "Location (Nungambakkam)",
    "locality_Kodambakkam": "Location (Kodambakkam)",
    "locality_OMR": "Location (OMR)",
    "furnishing_full": "Furnishing (Full)",
    "furnishing_semi": "Furnishing (Semi)",
    "furnishing_unfurnished": "Furnishing (Unfurnished)",
    "water_source_metro": "Water (Metro)",
    "water_source_borewell": "Water (Borewell)",
    "water_source_both": "Water (Both)",
}

OVERPRICING_THRESHOLD = 0.10   # 10% above predicted = overpriced
HIGH_STRESS_THRESHOLD = 0.40   # rent > 40% of income = high stress

# Load model and columns into memory
_model = None
_booster = None
_cols = None
_col_idx = None

try:
    with open(_MODEL_PATH, "rb") as f:
        _model = pickle.load(f)
        _booster = _model.get_booster() if hasattr(_model, "get_booster") else _model
    with open(_COLS_PATH, "rb") as f:
        _cols = pickle.load(f)
        _col_idx = {col: i for i, col in enumerate(_cols)}
except Exception as e:
    print(f"Error initializing Lambda model: {e}")


def validate_payload(data: dict) -> list:
    """Validate incoming property payload against boundary rules."""
    errors = []
    if "locality" not in data or data["locality"] not in VALID_LOCALITIES:
        errors.append(f"Invalid locality '{data.get('locality')}'. Valid: {VALID_LOCALITIES}")
    if "sqft" not in data or not (100 <= int(data["sqft"]) <= 10000):
        errors.append("sqft must be between 100 and 10000")
    if "bhk" not in data or int(data["bhk"]) not in [1, 2, 3, 4]:
        errors.append("bhk must be 1, 2, 3, or 4")
    if "furnishing" not in data or str(data["furnishing"]).lower() not in VALID_FURNISHING:
        errors.append(f"furnishing must be one of {VALID_FURNISHING}")
    if "water_source" not in data or str(data["water_source"]).lower() not in VALID_WATER_SOURCE:
        errors.append(f"water_source must be one of {VALID_WATER_SOURCE}")
    if "age" not in data or not (0 <= int(data["age"]) <= 50):
        errors.append("age must be between 0 and 50")
    return errors


def predict_and_explain(locality: str, sqft: int, bhk: int, furnishing: str, water_source: str, age: int):
    """Execute vector encoding, XGBoost prediction, and Tree SHAP explanation."""
    vec = np.zeros(len(_cols), dtype=np.float32)
    vec[_col_idx["sqft"]] = sqft
    vec[_col_idx["bhk"]] = bhk
    vec[_col_idx["age"]] = age

    loc_key = f"locality_{locality}"
    if loc_key in _col_idx:
        vec[_col_idx[loc_key]] = 1.0

    furn_key = f"furnishing_{furnishing}"
    if furn_key in _col_idx:
        vec[_col_idx[furn_key]] = 1.0

    water_key = f"water_source_{water_source}"
    if water_key in _col_idx:
        vec[_col_idx[water_key]] = 1.0

    dmatrix = xgb.DMatrix(vec.reshape(1, -1), feature_names=_cols)
    raw_pred = _booster.predict(dmatrix)[0]
    predicted_rent = max(0, round(int(raw_pred) / 500) * 500)

    # Native Tree SHAP: returns impact of each feature + bias as last element
    contribs = _booster.predict(dmatrix, pred_contribs=True)[0][:-1]
    raw_explanations = []
    for col, imp in zip(_cols, contribs):
        if abs(imp) >= 1.0:
            label = FEATURE_LABELS.get(col, col)
            raw_explanations.append({"feature": label, "raw_impact": float(imp)})

    raw_explanations.sort(key=lambda x: abs(x["raw_impact"]), reverse=True)
    top3 = []
    for item in raw_explanations[:3]:
        impact = round(item["raw_impact"])
        top3.append({
            "feature": item["feature"],
            "impact": impact,
            "direction": "increases" if impact > 0 else "decreases",
        })

    return predicted_rent, top3


def lambda_handler(event, context):
    """
    AWS Lambda invocation entrypoint.
    Supports both direct JSON payloads (boto3 invoke) and API Gateway / Function URL events.
    """
    if _booster is None or _cols is None:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"status": "error", "error": "Model failed to load during container initialization"}),
        }

    # Extract body whether called directly or through HTTP event
    body = event
    if isinstance(event, dict) and "body" in event and isinstance(event["body"], str):
        try:
            body = json.loads(event["body"])
        except json.JSONDecodeError:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"status": "error", "error": "Invalid JSON in request body"}),
            }

    # Validate inputs
    validation_errors = validate_payload(body)
    if validation_errors:
        return {
            "statusCode": 422,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"status": "error", "errors": validation_errors, "detail": " | ".join(validation_errors)}),
        }

    locality = body["locality"]
    sqft = int(body["sqft"])
    bhk = int(body["bhk"])
    furnishing = str(body["furnishing"]).lower()
    water_source = str(body["water_source"]).lower()
    age = int(body["age"])
    listed_rent = int(body["listed_rent"]) if body.get("listed_rent") is not None else None
    monthly_income = int(body["monthly_income"]) if body.get("monthly_income") is not None else None

    # Run inference + SHAP
    try:
        predicted_rent, explanations = predict_and_explain(locality, sqft, bhk, furnishing, water_source, age)
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"status": "error", "error": f"Inference execution failure: {str(e)}"}),
        }

    result = {
        "predicted_rent": predicted_rent,
        "explanation": explanations,
        "status": "ok",
    }

    # Overpricing calculation
    if listed_rent is not None:
        diff = listed_rent - predicted_rent
        diff_pct = diff / predicted_rent
        is_overpriced = diff_pct > OVERPRICING_THRESHOLD
        is_underpriced = diff_pct < -OVERPRICING_THRESHOLD

        if is_overpriced:
            label = "overpriced"
        elif is_underpriced:
            label = "good deal"
        else:
            label = "fair price"

        result["overpricing"] = {
            "listed_rent": listed_rent,
            "difference": diff,
            "difference_pct": round(diff_pct * 100, 1),
            "label": label,
            "is_overpriced": is_overpriced,
        }

    # Rent stress calculation
    if monthly_income is not None:
        rent_to_use = listed_rent if listed_rent else predicted_rent
        stress_ratio = rent_to_use / monthly_income

        if stress_ratio > HIGH_STRESS_THRESHOLD:
            stress_label = "high stress"
        elif stress_ratio > 0.25:
            stress_label = "moderate"
        else:
            stress_label = "comfortable"

        result["rent_stress"] = {
            "monthly_income": monthly_income,
            "rent_to_income": round(stress_ratio * 100, 1),
            "label": stress_label,
            "is_high_stress": stress_ratio > HIGH_STRESS_THRESHOLD,
        }

    # Human-readable verdict
    verdict_parts = []
    if "overpricing" in result:
        op = result["overpricing"]
        if op["is_overpriced"]:
            verdict_parts.append(f"Listed ₹{listed_rent:,} is {op['difference_pct']}% above market — overpriced.")
        elif op["label"] == "good deal":
            verdict_parts.append(f"Listed ₹{listed_rent:,} is {abs(op['difference_pct'])}% below market — good deal.")
        else:
            verdict_parts.append("Listed rent is fairly priced.")

    if "rent_stress" in result:
        rs = result["rent_stress"]
        verdict_parts.append(f"Rent is {rs['rent_to_income']}% of income ({rs['label']}).")

    if not verdict_parts:
        verdict_parts.append(f"Predicted market rent for this property is ₹{predicted_rent:,}.")

    result["verdict"] = " ".join(verdict_parts)

    # Return standard response format
    # If invoked directly via boto3, payload is parsed from body or returned cleanly
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(result),
        # also include direct attributes for direct boto3 lambda invoke convenience
        **result
    }
