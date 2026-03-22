"""
predictor.py
------------
This is the file the rest of your app will import.
It loads the trained model once and exposes:
  - predict_rent()              → just the number
  - predict_rent_with_shap()    → number + top 3 feature explanations
"""

import pickle
import os
import pandas as pd
import shap

# ── Paths ──────────────────────────────────────────────────────────────────────
_BASE_DIR   = os.path.dirname(__file__)
_MODEL_PATH = os.path.join(_BASE_DIR, "models", "rent_model.pkl")
_COLS_PATH  = os.path.join(_BASE_DIR, "models", "feature_columns.pkl")

# ── Human-readable feature name mapping ───────────────────────────────────────
# Converts encoded column names → something a user can read
_FEATURE_LABELS = {
    "sqft": "Property Size",
    "bhk":  "No. of Bedrooms",
    "age":  "Building Age",
    # locality
    "locality_Velachery":    "Location (Velachery)",
    "locality_Anna Nagar":   "Location (Anna Nagar)",
    "locality_Adyar":        "Location (Adyar)",
    "locality_T Nagar":      "Location (T Nagar)",
    "locality_Porur":        "Location (Porur)",
    "locality_Chromepet":    "Location (Chromepet)",
    "locality_Sholinganallur":"Location (Sholinganallur)",
    "locality_Perambur":     "Location (Perambur)",
    "locality_Korattur":     "Location (Korattur)",
    "locality_Medavakkam":   "Location (Medavakkam)",
    "locality_Tambaram":     "Location (Tambaram)",
    "locality_Mylapore":     "Location (Mylapore)",
    "locality_Nungambakkam": "Location (Nungambakkam)",
    "locality_Kodambakkam":  "Location (Kodambakkam)",
    "locality_OMR":          "Location (OMR)",
    # furnishing
    "furnishing_full":        "Furnishing (Full)",
    "furnishing_semi":        "Furnishing (Semi)",
    "furnishing_unfurnished": "Furnishing (Unfurnished)",
    # water
    "water_source_metro":    "Water (Metro)",
    "water_source_borewell": "Water (Borewell)",
    "water_source_both":     "Water (Both)",
}

# ── Load model + SHAP explainer ONCE ──────────────────────────────────────────
try:
    with open(_MODEL_PATH, "rb") as f:
        _model = pickle.load(f)
    with open(_COLS_PATH, "rb") as f:
        _feature_columns = pickle.load(f)

    # TreeExplainer is fast and works perfectly with XGBoost
    _explainer = shap.TreeExplainer(_model)
    _model_loaded = True
except FileNotFoundError:
    _model_loaded = False
    print("⚠️  Model files not found. Run train_model.py first.")


# ── Shared: build encoded DataFrame ───────────────────────────────────────────
def _build_df(locality, sqft, bhk, furnishing, water_source, age):
    input_data = {
        "sqft": [sqft],
        "bhk":  [bhk],
        "age":  [age],
        f"locality_{locality}":           [1],
        f"furnishing_{furnishing}":       [1],
        f"water_source_{water_source}":   [1],
    }
    df = pd.DataFrame(input_data)
    df = df.reindex(columns=_feature_columns, fill_value=0)
    return df


# ── predict_rent() — same as before, no SHAP ──────────────────────────────────
def predict_rent(locality, sqft, bhk, furnishing, water_source, age):
    if not _model_loaded:
        return {"error": "Model not loaded. Run train_model.py first.", "status": "error"}

    df = _build_df(locality, sqft, bhk, furnishing, water_source, age)
    raw = _model.predict(df)[0]
    predicted_rent = max(0, round(int(raw) / 500) * 500)

    return {"predicted_rent": predicted_rent, "status": "ok"}


# ── predict_rent_with_shap() — prediction + top 3 explanations ────────────────
def predict_rent_with_shap(locality, sqft, bhk, furnishing, water_source, age):
    """
    Returns predicted rent AND top 3 SHAP feature contributions.

    Returns
    -------
    dict — {
        "predicted_rent": 25000,
        "status": "ok",
        "explanation": [
            { "feature": "Location (Velachery)", "impact": 8000, "direction": "increases" },
            { "feature": "Property Size",         "impact": 5000, "direction": "increases" },
            { "feature": "Building Age",          "impact": -2000, "direction": "decreases" },
        ]
    }
    """
    if not _model_loaded:
        return {"error": "Model not loaded. Run train_model.py first.", "status": "error"}

    df = _build_df(locality, sqft, bhk, furnishing, water_source, age)

    # ── Predict ───────────────────────────────────────────────────────────────
    raw = _model.predict(df)[0]
    predicted_rent = max(0, round(int(raw) / 500) * 500)

    # ── SHAP values ───────────────────────────────────────────────────────────
    shap_values = _explainer(df)
    impacts     = shap_values.values[0]       # array of impact per feature
    columns     = df.columns.tolist()

    # ── Build explanation list ────────────────────────────────────────────────
    explanation_raw = []
    for col, impact in zip(columns, impacts):
        if abs(impact) < 1:          # skip near-zero contributions
            continue
        label = _FEATURE_LABELS.get(col, col)   # human-readable name
        explanation_raw.append({
            "feature":   label,
            "raw_impact": float(impact),
        })

    # Sort by absolute impact, keep top 3
    explanation_raw.sort(key=lambda x: abs(x["raw_impact"]), reverse=True)
    top3 = explanation_raw[:3]

    # ── Format for output ─────────────────────────────────────────────────────
    explanation = []
    for item in top3:
        impact = round(item["raw_impact"])
        explanation.append({
            "feature":   item["feature"],
            "impact":    impact,
            "direction": "increases" if impact > 0 else "decreases",
        })

    return {
        "predicted_rent": predicted_rent,
        "status":         "ok",
        "explanation":    explanation,
    }