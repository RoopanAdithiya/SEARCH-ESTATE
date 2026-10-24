"""
tests/test_db_and_api.py
------------------------
Automated regression tests verifying:
1. Database connectivity (SQLite fallback and PostgreSQL).
2. Alembic migration execution and stable primary key schema.
3. Property CRUD and duplicate detection (HTTP 409 for exact duplicates, allowing distinct units).
4. Rent prediction endpoint and baseline parity.
5. SHAP feature explanations integrity.
"""

import sys
from pathlib import Path
import pytest
from sqlalchemy import create_engine, text, inspect
from fastapi.testclient import TestClient

# Ensure backend root is on sys.path
_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from main import app
from database.db import engine, SessionLocal, DATABASE_URL
from models.property import Property

client = TestClient(app)


# ── 1. API Health Check ────────────────────────────────────────────────────────
def test_api_health_check():
    """Verify application startup and root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "Search Estate API" in data["message"]


# ── 2. Database Connectivity & Alembic Tests ───────────────────────────────────
def test_postgresql_connection_and_alembic_version():
    """Verify connection to PostgreSQL and presence of latest Alembic revision."""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1;")).scalar()
        assert result == 1

        # Check alembic_version table
        ver = conn.execute(text("SELECT version_num FROM alembic_version;")).scalar()
        assert ver is not None
        assert ver == "5cddc4bcdc3d"


def test_sqlite_fallback_capability(tmp_path):
    """Verify that SQLite engine operates cleanly as an offline fallback."""
    sqlite_db = tmp_path / "test_fallback.db"
    sqlite_url = f"sqlite:///{sqlite_db.as_posix()}"
    test_engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
    with test_engine.connect() as conn:
        res = conn.execute(text("SELECT 1;")).scalar()
        assert res == 1


def test_database_schema_and_stable_primary_key():
    """Verify properties table columns and stable integer primary key without hard DDL blocks."""
    insp = inspect(engine)
    assert "properties" in insp.get_table_names()

    col_names = [c["name"] for c in insp.get_columns("properties")]
    expected_cols = [
        "id", "locality", "sqft", "bhk", "furnishing", "water_source",
        "age", "rent", "bachelor_friendly", "pet_friendly", "lat", "lng"
    ]
    for col in expected_cols:
        assert col in col_names

    pk = insp.get_pk_constraint("properties")
    assert "id" in pk["constrained_columns"]


# ── 3. Property CRUD & Duplicate Prevention Tests ──────────────────────────────
def test_get_all_properties():
    """Verify retrieval of property listings."""
    response = client.get("/api/properties")
    assert response.status_code == 200
    props = response.json()
    assert isinstance(props, list)
    assert len(props) >= 15  # 15 migrated properties


def test_property_creation_and_duplicate_rejection():
    """Verify listing creation with coordinate auto-fill, duplicate rejection, and distinct unit support."""
    test_payload_1 = {
        "locality": "Medavakkam",
        "sqft": 1337,
        "bhk": 3,
        "furnishing": "semi",
        "water_source": "metro",
        "age": 4,
        "rent": 24999,
        "bachelor_friendly": True,
        "pet_friendly": False,
    }

    # Distinct unit with same locality, sqft, bhk, rent but different furnishing/age
    test_payload_2 = {
        "locality": "Medavakkam",
        "sqft": 1337,
        "bhk": 3,
        "furnishing": "full",
        "water_source": "metro",
        "age": 1,
        "rent": 24999,
        "bachelor_friendly": False,
        "pet_friendly": True,
    }

    # Clean up test properties if they exist
    db = SessionLocal()
    try:
        db.query(Property).filter(Property.rent == 24999).delete()
        db.commit()
    finally:
        db.close()

    created_ids = []
    try:
        # Step A: Add property 1
        resp1 = client.post("/api/add-property", json=test_payload_1)
        assert resp1.status_code == 200
        data1 = resp1.json()
        assert data1["locality"] == "Medavakkam"
        assert data1["rent"] == 24999
        assert data1["lat"] is not None
        assert data1["lng"] is not None
        created_ids.append(data1["id"])

        # Step B: Duplicate attempt with IDENTICAL attributes should return 409 Conflict
        resp_dup = client.post("/api/add-property", json=test_payload_1)
        assert resp_dup.status_code == 409
        assert "already exists" in resp_dup.json()["detail"].lower()

        # Step C: Distinct property with same locality/rent but different specs should be ACCEPTED
        resp2 = client.post("/api/add-property", json=test_payload_2)
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert data2["id"] != data1["id"]
        assert data2["furnishing"] == "full"
        created_ids.append(data2["id"])

    finally:
        # Cleanup test records
        db = SessionLocal()
        try:
            for pid in created_ids:
                prop = db.query(Property).filter(Property.id == pid).first()
                if prop:
                    db.delete(prop)
            db.commit()
        finally:
            db.close()


# ── 4. Rent Prediction Baseline & SHAP Parity Tests ────────────────────────────
BASELINE_CASES = [
    {
        "input": {"locality": "Velachery", "sqft": 1000, "bhk": 2, "furnishing": "semi", "water_source": "metro", "age": 5},
        "expected_rent": 25000,
    },
    {
        "input": {"locality": "Anna Nagar", "sqft": 1400, "bhk": 3, "furnishing": "full", "water_source": "metro", "age": 2},
        "expected_rent": 43500,
    },
    {
        "input": {"locality": "Tambaram", "sqft": 700, "bhk": 1, "furnishing": "unfurnished", "water_source": "borewell", "age": 12},
        "expected_rent": 13000,
    },
    {
        "input": {"locality": "Nungambakkam", "sqft": 2000, "bhk": 4, "furnishing": "full", "water_source": "both", "age": 1},
        "expected_rent": 57000,
    },
    {
        "input": {"locality": "Chromepet", "sqft": 900, "bhk": 2, "furnishing": "semi", "water_source": "metro", "age": 8},
        "expected_rent": 18000,
    },
]


@pytest.mark.parametrize("case", BASELINE_CASES)
def test_prediction_baseline_parity(case):
    """Verify prediction endpoint matches baseline trained model predictions."""
    payload = case["input"]
    response = client.post("/api/predict-rent", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["status"] == "ok"
    assert res["predicted_rent"] == case["expected_rent"]

    # Verify SHAP explanations are included and contain top 3 features
    assert "explanation" in res
    assert isinstance(res["explanation"], list)
    assert len(res["explanation"]) == 3
    for feat in res["explanation"]:
        assert "feature" in feat
        assert "impact" in feat
        assert feat["direction"] in ["increases", "decreases"]


def test_overpricing_and_rent_stress_calculation():
    """Verify overpricing delta and rent-stress ratios."""
    payload = {
        "locality": "Velachery",
        "sqft": 1000,
        "bhk": 2,
        "furnishing": "semi",
        "water_source": "metro",
        "age": 5,
        "listed_rent": 30000,   # Market is 25000 -> +20% overpriced
        "monthly_income": 60000, # 30000 / 60000 = 50% -> high stress
    }
    response = client.post("/api/predict-rent", json=payload)
    assert response.status_code == 200
    res = response.json()

    assert res["predicted_rent"] == 25000
    assert res["overpricing"] is not None
    assert res["overpricing"]["is_overpriced"] is True
    assert res["overpricing"]["difference_pct"] == 20.0
    assert res["overpricing"]["label"] == "overpriced"

    assert res["rent_stress"] is not None
    assert res["rent_stress"]["is_high_stress"] is True
    assert res["rent_stress"]["rent_to_income"] == 50.0
    assert res["rent_stress"]["label"] == "high stress"
