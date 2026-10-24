# models/property.py
from sqlalchemy import Column, Integer, String, Boolean, Float
from database.db import Base

class Property(Base):
    __tablename__ = "properties"

    # Primary stable identifier
    id           = Column(Integer, primary_key=True, index=True)
    locality     = Column(String, index=True)
    sqft         = Column(Integer)
    bhk          = Column(Integer)
    furnishing   = Column(String)
    water_source = Column(String)
    age          = Column(Integer)
    rent         = Column(Integer)

    bachelor_friendly = Column(Boolean, default=False)
    pet_friendly      = Column(Boolean, default=False)

    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
