import os
import hashlib
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from argon2.low_level import hash_secret, Type


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
    pepper = os.getenv("CREDENTIAL_SALT", "")
    # derive a deterministic per-user salt
    salt = hashlib.sha256(f"{pepper}:{username}".encode()).digest()[:16]
    data = f"{username}:{password}".encode()
    return hash_secret(
        data,
        salt,
        time_cost=2,
        memory_cost=102400,
        parallelism=8,
        hash_len=32,
        type=Type.ID,
    ).decode()


def init_db(url: str | None = None):
    global engine, SessionLocal
    if url:
        engine = create_engine(url, future=True)
        SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    return SessionLocal()
