"""
train_model.py
--------------
Trains an XGBoost Regressor on the rent dataset.
Saves the trained model + feature columns to the models/ folder.

Run AFTER generate_dataset.py:
    python train_model.py
"""

import pandas as pd
import numpy as np
import pickle
import os
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

# ── 1. Load data ───────────────────────────────────────────────────────────────
DATA_PATH  = "data/rent_data.csv"
MODEL_DIR  = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "rent_model.pkl")
COLS_PATH  = os.path.join(MODEL_DIR, "feature_columns.pkl")

os.makedirs(MODEL_DIR, exist_ok=True)

df = pd.read_csv(DATA_PATH)
print(f"📂 Loaded {len(df)} rows from {DATA_PATH}")

# ── 2. Encode categorical columns (one-hot encoding) ──────────────────────────
# Machines only understand numbers, not "semi-furnished vibes"
df_encoded = pd.get_dummies(df, columns=["locality", "furnishing", "water_source"])

print(f"🔢 Features after encoding: {df_encoded.shape[1] - 1} columns")

# ── 3. Split features (X) and target (y) ─────────────────────────────────────
X = df_encoded.drop(columns=["rent"])
y = df_encoded["rent"]

# Save the exact column names — CRITICAL for prediction later
feature_columns = X.columns.tolist()

# ── 4. Train / test split (80% train, 20% test) ───────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"🏋️  Training on {len(X_train)} rows | Testing on {len(X_test)} rows")

# ── 5. Train XGBoost model ────────────────────────────────────────────────────
model = XGBRegressor(
    n_estimators=200,       # number of trees
    learning_rate=0.05,     # how much each tree corrects the last
    max_depth=5,            # how deep each tree goes
    subsample=0.8,          # use 80% of data per tree (reduces overfitting)
    colsample_bytree=0.8,   # use 80% of features per tree
    random_state=42,
    verbosity=0,
)

model.fit(X_train, y_train)
print("✅ Model trained!")

# ── 6. Evaluate ───────────────────────────────────────────────────────────────
y_pred = model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
r2  = r2_score(y_test, y_pred)

print(f"\n📊 Model Performance:")
print(f"   MAE (Mean Absolute Error) : ₹{mae:,.0f}")
print(f"   R² Score                  : {r2:.3f}  (1.0 = perfect, >0.85 = good)")

# Show a few predictions vs actuals
print("\n🔍 Sample predictions vs actual:")
comparison = pd.DataFrame({"Actual": y_test.values[:8], "Predicted": y_pred[:8].astype(int)})
print(comparison.to_string(index=False))

# ── 7. Save model + feature columns ──────────────────────────────────────────
with open(MODEL_PATH, "wb") as f:
    pickle.dump(model, f)

with open(COLS_PATH, "wb") as f:
    pickle.dump(feature_columns, f)

print(f"\n💾 Model saved       → {MODEL_PATH}")
print(f"💾 Feature cols saved → {COLS_PATH}")
print("\n🎉 Done! You can now use predict.py to test predictions.")