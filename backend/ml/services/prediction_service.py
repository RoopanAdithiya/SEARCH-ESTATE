"""
ml/services/prediction_service.py
----------------------------------
The "brain" layer between your API and the raw model.

Calls predictor.predict_rent() and adds:
  - overpricing flag
  - rent stress score
  - effective monthly cost
  - human-readable verdict

Your FastAPI route imports from HERE, not from predictor.py directly.
"""

from ml.predictor import predict_rent_with_shap


# ── Constants ─────────────────────────────────────────────────────────────────
OVERPRICING_THRESHOLD = 0.10   # 10% above predicted = overpriced
HIGH_STRESS_THRESHOLD = 0.40   # rent > 40% of income = high stress (standard rule)


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

    Parameters
    ----------
    locality, sqft, bhk, furnishing, water_source, age : property details
    listed_rent    : int (optional) — what the landlord is asking
    monthly_income : int (optional) — tenant's income for stress calculation

    Returns
    -------
    dict with predicted_rent, overpricing analysis, rent stress, verdict
    """

    # ── Step 1: Get predicted rent + SHAP explanation ────────────────────────
    prediction = predict_rent_with_shap(
        locality=locality,
        sqft=sqft,
        bhk=bhk,
        furnishing=furnishing,
        water_source=water_source,
        age=age,
    )

    if prediction["status"] == "error":
        return prediction   # bubble up model errors

    predicted_rent = prediction["predicted_rent"]
    result = {
        "predicted_rent": predicted_rent,
        "explanation":    prediction.get("explanation", []),
        "status": "ok",
    }

    # ── Step 2: Overpricing analysis (only if listed_rent is provided) ────────
    if listed_rent is not None:
        difference     = listed_rent - predicted_rent
        diff_pct       = difference / predicted_rent          # e.g. 0.15 = 15% over

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
            "difference_pct":    round(diff_pct * 100, 1),   # e.g. 15.0 (%)
            "label":             overpricing_label,
            "is_overpriced":     is_overpriced,
        }

    # ── Step 3: Rent stress (only if monthly_income is provided) ─────────────
    if monthly_income is not None:
        rent_to_use   = listed_rent if listed_rent else predicted_rent
        stress_ratio  = rent_to_use / monthly_income          # e.g. 0.35 = 35%

        if stress_ratio > HIGH_STRESS_THRESHOLD:
            stress_label = "high stress"
        elif stress_ratio > 0.25:
            stress_label = "moderate"
        else:
            stress_label = "comfortable"

        result["rent_stress"] = {
            "monthly_income":  monthly_income,
            "rent_to_income":  round(stress_ratio * 100, 1),  # e.g. 35.0 (%)
            "label":           stress_label,
            "is_high_stress":  stress_ratio > HIGH_STRESS_THRESHOLD,
        }

    # ── Step 4: Human-readable verdict ───────────────────────────────────────
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
            verdict_parts.append(f"Listed rent is fairly priced.")

    if "rent_stress" in result:
        rs = result["rent_stress"]
        verdict_parts.append(
            f"Rent is {rs['rent_to_income']}% of income ({rs['label']})."
        )

    if not verdict_parts:
        verdict_parts.append(f"Predicted market rent for this property is ₹{predicted_rent:,}.")

    result["verdict"] = " ".join(verdict_parts)

    return result