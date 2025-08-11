import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import hashlib


def _build_url() -> str:
    if url := os.getenv("DATABASE_URL"):
        return url
    host = os.getenv("DB_HOST")
    name = os.getenv("DB_NAME")
    if host and name:
        user = os.getenv("DB_USER", "")
        password = os.getenv("DB_PASSWORD", "")
        port = os.getenv("DB_PORT", "")
        auth = f"{user}:{password}@" if user else ""
        port_part = f":{port}" if port else ""
        return f"postgresql://{auth}{host}{port_part}/{name}"
    return "sqlite:///bot.db"


DATABASE_URL = _build_url()

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def hash_credentials(username: str, password: str) -> str:
    return hashlib.sha256(f"{username}:{password}".encode()).hexdigest()


def init_db(url: str | None = None):
    global engine, SessionLocal
    if url:
        engine = create_engine(url, future=True)
        SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    return SessionLocal()
