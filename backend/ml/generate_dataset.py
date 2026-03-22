"""
generate_dataset.py
-------------------
Run this ONCE to create a fake-but-realistic Chennai rent dataset.
Output: backend/ml/data/rent_data.csv

Usage:
    python generate_dataset.py
"""

import pandas as pd
import numpy as np
import os

np.random.seed(42)

# ── Config ────────────────────────────────────────────────────────────────────
N = 300  # number of rows (feel free to increase later)

localities = [
    "Velachery", "Anna Nagar", "Adyar", "T Nagar", "Porur",
    "Chromepet", "Sholinganallur", "Perambur", "Korattur", "Medavakkam",
    "Tambaram", "Mylapore", "Nungambakkam", "Kodambakkam", "OMR"
]

# Base rent multiplier per locality (premium areas cost more)
locality_multiplier = {
    "Anna Nagar": 1.35, "Adyar": 1.40, "T Nagar": 1.30,
    "Nungambakkam": 1.45, "Mylapore": 1.25, "Sholinganallur": 1.20,
    "OMR": 1.15, "Velachery": 1.10, "Porur": 1.05, "Kodambakkam": 1.10,
    "Chromepet": 0.90, "Tambaram": 0.85, "Medavakkam": 0.95,
    "Perambur": 0.88, "Korattur": 0.87,
}

furnishing_multiplier = {"full": 1.20, "semi": 1.05, "unfurnished": 1.0}
water_multiplier = {"metro": 1.05, "borewell": 1.0, "both": 1.08}

# ── Generate rows ─────────────────────────────────────────────────────────────
rows = []
for _ in range(N):
    locality     = np.random.choice(localities)
    sqft         = int(np.random.choice([600, 700, 800, 900, 1000, 1100, 1200, 1400, 1600, 2000]))
    bhk          = np.random.choice([1, 2, 3, 4], p=[0.20, 0.45, 0.28, 0.07])
    furnishing   = np.random.choice(["full", "semi", "unfurnished"], p=[0.30, 0.45, 0.25])
    water_source = np.random.choice(["metro", "borewell", "both"], p=[0.50, 0.30, 0.20])
    age          = int(np.random.randint(0, 20))   # building age in years

    # Base rent formula (keep it simple & realistic)
    base_rent = (sqft * 18) + (bhk * 1500)
    base_rent *= locality_multiplier[locality]
    base_rent *= furnishing_multiplier[furnishing]
    base_rent *= water_multiplier[water_source]
    base_rent *= max(0.75, 1 - age * 0.012)       # older building → slightly lower rent

    # Add realistic noise
    noise = np.random.normal(0, 0.07)
    rent = int(base_rent * (1 + noise))
    rent = max(5000, round(rent / 500) * 500)      # round to nearest ₹500, min ₹5000

    rows.append({
        "locality":     locality,
        "sqft":         sqft,
        "bhk":          bhk,
        "furnishing":   furnishing,
        "water_source": water_source,
        "age":          age,
        "rent":         rent,
    })

# ── Save ──────────────────────────────────────────────────────────────────────
os.makedirs("data", exist_ok=True)
df = pd.DataFrame(rows)
df.to_csv("data/rent_data.csv", index=False)

print(f"✅ Dataset saved → data/rent_data.csv  ({len(df)} rows)")
print(df.head(10).to_string(index=False))
print(f"\nRent range: ₹{df['rent'].min():,} – ₹{df['rent'].max():,}")