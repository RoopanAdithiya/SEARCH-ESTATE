"""
ml/utils/preprocess.py
----------------------
All preprocessing logic lives here.
Both train_model.py and predictor.py import from this file.
This way, training and prediction ALWAYS use identical logic.
"""

import pandas as pd

# ── Valid values (used for input validation) ───────────────────────────────────
VALID_LOCALITIES = [
    "Velachery", "Anna Nagar", "Adyar", "T Nagar", "Porur",
    "Chromepet", "Sholinganallur", "Perambur", "Korattur", "Medavakkam",
    "Tambaram", "Mylapore", "Nungambakkam", "Kodambakkam", "OMR"
]
VALID_FURNISHING    = ["full", "semi", "unfurnished"]
VALID_WATER_SOURCE  = ["metro", "borewell", "both"]


def validate_input(locality, sqft, bhk, furnishing, water_source, age):
    """
    Validates prediction inputs before passing to model.
    Raises ValueError with a clear message if anything is wrong.
    """
    errors = []

    if locality not in VALID_LOCALITIES:
        errors.append(f"Invalid locality '{locality}'. Valid: {VALID_LOCALITIES}")
    if not (100 <= sqft <= 10000):
        errors.append(f"sqft must be between 100 and 10000. Got: {sqft}")
    if bhk not in [1, 2, 3, 4]:
        errors.append(f"bhk must be 1, 2, 3, or 4. Got: {bhk}")
    if furnishing not in VALID_FURNISHING:
        errors.append(f"furnishing must be one of {VALID_FURNISHING}. Got: {furnishing}")
    if water_source not in VALID_WATER_SOURCE:
        errors.append(f"water_source must be one of {VALID_WATER_SOURCE}. Got: {water_source}")
    if not (0 <= age <= 50):
        errors.append(f"age must be between 0 and 50. Got: {age}")

    if errors:
        raise ValueError(" | ".join(errors))


def encode_input(locality, sqft, bhk, furnishing, water_source, age, feature_columns):
    """
    Converts raw input into a one-hot encoded DataFrame
    that matches the exact columns the model was trained on.

    Parameters
    ----------
    feature_columns : list — the saved column list from training

    Returns
    -------
    pd.DataFrame — single row, ready for model.predict()
    """
    raw = {
        "sqft": [sqft],
        "bhk":  [bhk],
        "age":  [age],
        f"locality_{locality}":         [1],
        f"furnishing_{furnishing}":     [1],
        f"water_source_{water_source}": [1],
    }

    df = pd.DataFrame(raw)

    # Fill any missing dummy columns with 0
    df = df.reindex(columns=feature_columns, fill_value=0)

    return df


def preprocess_dataframe(df):
    """
    Encodes a full training DataFrame.
    Used by train_model.py.

    Parameters
    ----------
    df : pd.DataFrame — raw dataset with categorical columns

    Returns
    -------
    X : pd.DataFrame — features (encoded)
    y : pd.Series    — target (rent)
    feature_columns : list — column names to save alongside model
    """
    df_encoded = pd.get_dummies(df, columns=["locality", "furnishing", "water_source"])

    X = df_encoded.drop(columns=["rent"])
    y = df_encoded["rent"]
    feature_columns = X.columns.tolist()

    return X, y, feature_columns