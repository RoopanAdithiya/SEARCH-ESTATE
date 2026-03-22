from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ── Change this to your PostgreSQL credentials ─────────────────────────────────
# Format: postgresql://username:password@host/database_name
DATABASE_URL = "postgresql://postgres:roopan%40123@localhost/searchestate"

# check_same_thread is SQLite-only — PostgreSQL doesn't need it
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()