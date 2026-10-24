"""
ml/services/prediction_service.py
----------------------------------
The local prediction layer between the API and the trained rent model.
Adds overpricing detection, rent stress ratio, and human-readable verdicts.
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
    Full property analysis — local prediction + intelligence layer.
    """
    prediction = predict_rent_with_shap(
        locality=locality,
        sqft=sqft,
        bhk=bhk,
        furnishing=furnishing,
        water_source=water_source,
        age=age,
    )
    if prediction.get("status") == "error":
        return prediction

    predicted_rent = prediction["predicted_rent"]
    result = {
        "predicted_rent": predicted_rent,
        "explanation":    prediction.get("explanation", []),
        "status":         "ok",
        "provider":       "local",
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
