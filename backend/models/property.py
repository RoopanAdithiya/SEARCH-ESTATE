# models/property.py
# SQLAlchemy model — defines the "properties" table in your DB

from sqlalchemy import Column, Integer, String, Boolean
from database.db import Base

class Property(Base):
    __tablename__ = "properties"

    id           = Column(Integer, primary_key=True, index=True)
    locality     = Column(String)
    sqft         = Column(Integer)
    bhk          = Column(Integer)
    furnishing   = Column(String)
    water_source = Column(String)
    age          = Column(Integer)
    rent         = Column(Integer)   # what the landlord is listing it at

    bachelor_friendly = Column(Boolean, default=False)
    pet_friendly      = Column(Boolean, default=False)