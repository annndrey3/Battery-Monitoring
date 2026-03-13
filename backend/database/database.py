from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database URL (PostgreSQL or SQLite)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./battery_monitoring.db")

# SQLite требует connect_args, PostgreSQL - нет
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def is_sqlite():
    """Проверка, используется ли SQLite"""
    return DATABASE_URL.startswith("sqlite")
