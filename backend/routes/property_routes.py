# routes/property_routes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.session import get_db
from models.property import Property
from schemas.property_schema import PropertyCreate, PropertyResponse
from ml.services.prediction_service import analyze_property as ai_analyze

router = APIRouter(prefix="/api", tags=["Properties"])

# ── Locality → coordinates lookup ─────────────────────────────────────────────
LOCALITY_COORDS = {
    "Velachery":      (12.9815, 80.2180),
    "Anna Nagar":     (13.0850, 80.2101),
    "Adyar":          (13.0012, 80.2565),
    "T Nagar":        (13.0418, 80.2341),
    "Porur":          (13.0368, 80.1573),
    "Chromepet":      (12.9516, 80.1462),
    "Sholinganallur": (12.9010, 80.2279),
    "Perambur":       (13.1143, 80.2329),
    "Korattur":       (13.1103, 80.1863),
    "Medavakkam":     (12.9255, 80.1982),
    "Tambaram":       (12.9249, 80.1000),
    "Mylapore":       (13.0368, 80.2676),
    "Nungambakkam":   (13.0569, 80.2425),
    "Kodambakkam":    (13.0524, 80.2270),
    "OMR":            (12.9121, 80.2275),
}


# ── 1. Add a property listing ─────────────────────────────────────────────────
@router.post("/add-property", response_model=PropertyResponse)
def add_property(data: PropertyCreate, db: Session = Depends(get_db)):
    prop_data = data.dict()

    # Auto-fill lat/lng from locality
    coords = LOCALITY_COORDS.get(data.locality)
    if coords:
        prop_data["lat"] = coords[0]
        prop_data["lng"] = coords[1]

    prop = Property(**prop_data)
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return prop


# ── 2. Get all properties ─────────────────────────────────────────────────────
@router.get("/properties")
def get_properties(db: Session = Depends(get_db)):
    return db.query(Property).all()


# ── 3. Backfill existing properties that have no lat/lng ──────────────────────
@router.post("/backfill-coords")
def backfill_coords(db: Session = Depends(get_db)):
    """
    One-time endpoint — fills lat/lng for properties added before this feature.
    Call once from /docs, then forget about it.
    """
    props = db.query(Property).filter(Property.lat == None).all()
    updated = 0
    for p in props:
        coords = LOCALITY_COORDS.get(p.locality)
        if coords:
            p.lat = coords[0]
            p.lng = coords[1]
            updated += 1
    db.commit()
    return {"updated": updated, "message": f"Backfilled {updated} properties"}


# ── 4. AI analysis of a stored property ──────────────────────────────────────
@router.get("/analyze/{property_id}")
def analyze_property(property_id: int, db: Session = Depends(get_db)):
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
        listed_rent=prop.rent,
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
            "lat":           prop.lat,
            "lng":           prop.lng,
        },
        "analysis": result,
    }