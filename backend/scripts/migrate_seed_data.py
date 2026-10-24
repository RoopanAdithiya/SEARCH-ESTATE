"""
scripts/migrate_seed_data.py
----------------------------
Non-destructive data inventory, normalization, and deduplication migration tool.
Safely migrates properties from legacy SQLite (app.db) into the configured target
database (local PostgreSQL or Amazon RDS PostgreSQL) without deleting or overwriting
existing records.
"""

import sys
import sqlite3
from pathlib import Path
from sqlalchemy.orm import Session

# Add backend directory to sys.path
_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from database.db import SessionLocal, engine, DATABASE_URL
from models.property import Property
from routes.property_routes import LOCALITY_COORDS

# Standard valid values matching preprocessing pipeline
VALID_WATER_SOURCES = {
    "metro": "metro",
    "borewell": "borewell",
    "both": "both",
    "bore": "borewell",
    "yes": "metro",  # Map legacy 'yes' to default metro
}


def get_sqlite_properties(sqlite_path: Path):
    """Read properties directly from SQLite file safely (read-only)."""
    if not sqlite_path.exists():
        print(f"⚠️  SQLite file not found at {sqlite_path}")
        return []

    con = sqlite3.connect(sqlite_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    try:
        cur.execute("SELECT * FROM properties ORDER BY id ASC")
        rows = [dict(r) for r in cur.fetchall()]
    except Exception as e:
        print(f"⚠️  Error reading SQLite properties: {e}")
        rows = []
    finally:
        con.close()
    return rows


def normalize_record(record: dict) -> dict:
    """Normalize fields, fix casing, validate water source and fill coordinates."""
    # Locality normalization
    raw_loc = record.get("locality", "").strip()
    # Match against known locality coordinates case-insensitively
    matched_loc = None
    for loc in LOCALITY_COORDS:
        if loc.lower() == raw_loc.lower():
            matched_loc = loc
            break
    locality = matched_loc or raw_loc.title()

    # Coordinates
    lat = record.get("lat")
    lng = record.get("lng")
    if (lat is None or lng is None) and locality in LOCALITY_COORDS:
        coords = LOCALITY_COORDS[locality]
        lat, lng = coords[0], coords[1]

    # Water source normalization
    raw_water = str(record.get("water_source", "metro")).lower().strip()
    water_source = VALID_WATER_SOURCES.get(raw_water, "metro")

    return {
        "locality": locality,
        "sqft": int(record["sqft"]),
        "bhk": int(record["bhk"]),
        "furnishing": str(record.get("furnishing", "semi")).lower().strip(),
        "water_source": water_source,
        "age": int(record.get("age", 5)),
        "rent": int(record["rent"]),
        "bachelor_friendly": bool(record.get("bachelor_friendly", False)),
        "pet_friendly": bool(record.get("pet_friendly", False)),
        "lat": lat,
        "lng": lng,
    }


def run_migration(dry_run: bool = False):
    """Execute non-destructive migration."""
    print("=" * 65)
    print("📦  Search Estate: Database Inventory & Migration")
    print("=" * 65)
    print(f"Target Database Engine: {engine.dialect.name}")
    masked_url = DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL
    print(f"Target Database Host:   {masked_url}")
    print(f"Execution Mode:         {'DRY RUN (No changes)' if dry_run else 'APPLY CHANGES'}")
    print("-" * 65)

    sqlite_path = _backend_dir / "app.db"
    sqlite_records = get_sqlite_properties(sqlite_path)
    print(f"Found {len(sqlite_records)} records in SQLite ({sqlite_path.name})")

    db: Session = SessionLocal()
    try:
        existing_target_props = db.query(Property).all()
        print(f"Found {len(existing_target_props)} records in Target Database ({engine.dialect.name})")

        # Build set of existing keys in target: (locality.lower(), sqft, bhk, rent)
        existing_keys = {
            (p.locality.lower(), p.sqft, p.bhk, p.rent) for p in existing_target_props
        }

        migrated_count = 0
        skipped_count = 0
        duplicate_count = 0

        print("\nProcessing SQLite records for migration:")
        for r in sqlite_records:
            norm = normalize_record(r)
            key = (norm["locality"].lower(), norm["sqft"], norm["bhk"], norm["rent"])

            if key in existing_keys:
                print(f"  ⏭️  Skip: {norm['locality']} {norm['sqft']}sqft {norm['bhk']}BHK (₹{norm['rent']:,}) already exists.")
                duplicate_count += 1
                skipped_count += 1
                continue

            if not dry_run:
                new_prop = Property(**norm)
                db.add(new_prop)
                db.flush()  # assign ID without committing yet
                existing_keys.add(key)
                print(f"  ✅ Added: ID #{new_prop.id} - {norm['locality']} {norm['sqft']}sqft {norm['bhk']}BHK (₹{norm['rent']:,})")
            else:
                existing_keys.add(key)
                print(f"  [DRY RUN] Would Add: {norm['locality']} {norm['sqft']}sqft {norm['bhk']}BHK (₹{norm['rent']:,})")

            migrated_count += 1

        if not dry_run:
            db.commit()
            print("\n💾 Changes committed successfully.")
        else:
            db.rollback()
            print("\n[DRY RUN] No database changes committed.")

        final_count = db.query(Property).count()
        print("-" * 65)
        print("📊 Migration Summary:")
        print(f"   SQLite Source Count:     {len(sqlite_records)}")
        print(f"   Target Initial Count:    {len(existing_target_props)}")
        print(f"   New Records Migrated:    {migrated_count}")
        print(f"   Skipped / Duplicates:    {skipped_count}")
        print(f"   Target Final Count:      {final_count}")
        print("=" * 65)

    except Exception as e:
        db.rollback()
        print(f"\n❌ Migration failed with error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    is_dry_run = "--dry-run" in sys.argv
    run_migration(dry_run=is_dry_run)
