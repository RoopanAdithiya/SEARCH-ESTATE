"""
database/db.py
--------------
Database connection configuration and SQLAlchemy initialization.
Dynamically reads DATABASE_URL from environment variables with fallback
to local SQLite for seamless offline development.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load environment variables from .env file
# Looks in current working directory and backend directory
_backend_dir = Path(__file__).resolve().parent.parent
load_dotenv(_backend_dir / ".env")
load_dotenv()

# Read DATABASE_URL or fall back to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# Default to local SQLite if empty or not configured
if not DATABASE_URL:
    sqlite_path = _backend_dir / "app.db"
    DATABASE_URL = f"sqlite:///{sqlite_path.as_posix()}"

# Normalize legacy postgres:// URI to standard postgresql:// for SQLAlchemy
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Configure engine arguments based on dialect
if "sqlite" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
else:
    # PostgreSQL / Amazon RDS configuration
    # pool_pre_ping checks connection liveness before queries
    # pool_recycle refreshes connections every 5 minutes to prevent stale idle timeouts
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
