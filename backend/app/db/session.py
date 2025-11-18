"""SQLAlchemy session/engine placeholder.
Fill in actual engine configuration in Phase 1.
"""
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL: Optional[str] = None  # set from settings at runtime

engine = create_engine(DATABASE_URL or "sqlite+pysqlite:///:memory:", echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
