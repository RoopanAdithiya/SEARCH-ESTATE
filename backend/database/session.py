# database/session.py
# Provides get_db() — used in every route that needs DB access

from database.db import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()