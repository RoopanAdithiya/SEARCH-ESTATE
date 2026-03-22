"""
main.py
-------
FastAPI app entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.predict import router as predict_router
from routes.property_routes import router as property_router

# ── Create DB tables on startup (safe to run multiple times) ──────────────────
from database.db import Base, engine
import models.property  # must import so SQLAlchemy knows about the table
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Search Estate API",
    description="AI-powered real estate search with rent prediction",
    version="1.0.0",
)

# ── CORS (so your frontend can call the API) ──────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten this in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(predict_router)
app.include_router(property_router)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "ok", "message": "Search Estate API is running"}