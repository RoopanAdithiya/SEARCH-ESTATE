# schemas/property_schema.py
# Pydantic schemas — define what the API accepts and returns

from pydantic import BaseModel
from typing import Optional

# ── What the landlord sends when adding a property ────────────────────────────
class PropertyCreate(BaseModel):
    locality:     str
    sqft:         int
    bhk:          int
    furnishing:   str
    water_source: str
    age:          int
    rent:         int
    bachelor_friendly: bool = False
    pet_friendly:      bool = False

# ── What the API returns after saving (includes the generated id) ─────────────
class PropertyResponse(PropertyCreate):
    id: int

    class Config:
        from_attributes = True  # allows reading from SQLAlchemy model directly