import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from core.config import DATABASE_URL

# Get DB URL from config
db_url = DATABASE_URL

if not db_url:
    raise ValueError("DATABASE_URL is not set in environment variables")

# Fix Render / Heroku postgres prefix issue
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# Mask credentials for logging
def mask_db_url(url: str):
    try:
        if "@" in url:
            return "****:****@" + url.split("@")[1]
        return url
    except Exception:
        return "Database URL"

print(f"Connecting to database: {mask_db_url(db_url)}")

# Create SQLAlchemy engine
engine = create_engine(
    db_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={"connect_timeout": 10}
)

# Session maker
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base model
Base = declarative_base()


# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()