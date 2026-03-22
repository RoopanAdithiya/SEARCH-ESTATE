"""
routes/predict.py
-----------------
FastAPI router for rent prediction endpoint.

Registered in main.py like:
    from routes.predict import router
    app.include_router(router)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from ml.services.prediction_service import analyze_property

router = APIRouter(prefix="/api", tags=["Predictions"])


# ── Request schema ─────────────────────────────────────────────────────────────
class PredictRequest(BaseModel):
    locality:     str = Field(..., example="Velachery")
    sqft:         int = Field(..., gt=0, example=1000)
    bhk:          int = Field(..., ge=1, le=4, example=2)
    furnishing:   str = Field(..., example="semi")
    water_source: str = Field(..., example="metro")
    age:          int = Field(..., ge=0, example=5)

    # Optional fields for deeper analysis
    listed_rent:    Optional[int] = Field(None, example=27000)
    monthly_income: Optional[int] = Field(None, example=60000)


# ── Response schema ────────────────────────────────────────────────────────────
class PredictResponse(BaseModel):
    predicted_rent: int
    verdict:        str
    status:         str
    overpricing:    Optional[dict] = None
    rent_stress:    Optional[dict] = None


# ── Endpoint ───────────────────────────────────────────────────────────────────
@router.post("/predict-rent", response_model=PredictResponse)
def predict_rent_endpoint(data: PredictRequest):
    """
    Predict fair market rent for a property.

    - **predicted_rent** : model's estimate of fair rent
    - **overpricing**    : comparison vs listed_rent (if provided)
    - **rent_stress**    : affordability analysis (if monthly_income provided)
    - **verdict**        : human-readable summary
    """
    try:
        result = analyze_property(
            locality=data.locality,
            sqft=data.sqft,
            bhk=data.bhk,
            furnishing=data.furnishing,
            water_source=data.water_source,
            age=data.age,
            listed_rent=data.listed_rent,
            monthly_income=data.monthly_income,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("error"))

    return result