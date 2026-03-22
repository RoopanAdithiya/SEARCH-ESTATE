# routes/property_routes.py
# Two endpoints:
#   POST /api/add-property      → landlord adds a listing
#   GET  /api/analyze/{id}      → AI analyzes a stored property

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.session import get_db
from models.property import Property
from schemas.property_schema import PropertyCreate, PropertyResponse
from ml.services.prediction_service import analyze_property as ai_analyze

router = APIRouter(prefix="/api", tags=["Properties"])


# ── 1. Add a property listing ─────────────────────────────────────────────────
@router.post("/add-property", response_model=PropertyResponse)
def add_property(data: PropertyCreate, db: Session = Depends(get_db)):
    """
    Landlord submits a property listing.
    Stores it in the DB and returns it with its generated ID.
    """
    prop = Property(**data.dict())
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return prop


# ── 2. Get all properties ─────────────────────────────────────────────────────
@router.get("/properties")
def get_properties(db: Session = Depends(get_db)):
    """
    Returns all stored property listings.
    """
    return db.query(Property).all()


# ── 3. AI analysis of a stored property ──────────────────────────────────────
@router.get("/analyze/{property_id}")
def analyze_property(property_id: int, db: Session = Depends(get_db)):
    """
    Fetches a property from DB by ID, runs it through the AI model,
    and returns the full analysis: predicted rent, overpricing, verdict.
    """
    prop = db.query(Property).filter(Property.id == property_id).first()

    if not prop:
        raise HTTPException(status_code=404, detail=f"Property {property_id} not found")

    result = ai_analyze(
        locality=prop.locality,
        sqft=prop.sqft,
        bhk=prop.bhk,
        furnishing=prop.furnishing,
        water_source=prop.water_source,
        age=prop.age,
        listed_rent=prop.rent,   # compare AI prediction vs what landlord listed
    )

    return {
        "property": {
            "id":            prop.id,
            "locality":      prop.locality,
            "sqft":          prop.sqft,
            "bhk":           prop.bhk,
            "furnishing":    prop.furnishing,
            "water_source":  prop.water_source,
            "age":           prop.age,
            "listed_rent":   prop.rent,
            "bachelor_friendly": prop.bachelor_friendly,
            "pet_friendly":      prop.pet_friendly,
        },
        "analysis": result,
    }