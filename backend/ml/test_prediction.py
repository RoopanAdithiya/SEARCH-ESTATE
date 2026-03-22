"""
test_prediction.py
------------------
Run this to verify everything works end-to-end.

Usage:
    python test_prediction.py
"""

from predictor import predict_rent

# ── Test cases ────────────────────────────────────────────────────────────────
test_cases = [
    {"locality": "Velachery",     "sqft": 1000, "bhk": 2, "furnishing": "semi",        "water_source": "metro",    "age": 5},
    {"locality": "Anna Nagar",    "sqft": 1400, "bhk": 3, "furnishing": "full",        "water_source": "metro",    "age": 2},
    {"locality": "Tambaram",      "sqft": 700,  "bhk": 1, "furnishing": "unfurnished", "water_source": "borewell", "age": 12},
    {"locality": "Nungambakkam",  "sqft": 2000, "bhk": 4, "furnishing": "full",        "water_source": "both",     "age": 1},
    {"locality": "Chromepet",     "sqft": 900,  "bhk": 2, "furnishing": "semi",        "water_source": "metro",    "age": 8},
]

print("=" * 55)
print("🏠  Rent Prediction Test")
print("=" * 55)

for tc in test_cases:
    result = predict_rent(**tc)
    rent = result.get("predicted_rent", "ERROR")
    print(
        f"  {tc['locality']:<16} | {tc['sqft']} sqft | {tc['bhk']}BHK | "
        f"{tc['furnishing']:<12} → ₹{rent:,}"
    )

print("=" * 55)
print("✅ All predictions done!")