import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get DB URL from environment variables
db_url = os.environ.get("DATABASE_URL")

if not db_url:
    # Attempt to construct from individual components if DATABASE_URL is missing
    user = os.getenv("DB_USERNAME")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOSTNAME")
    port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_DATABASE")
    
    if all([user, password, host, db_name]):
        db_url = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
    else:
        raise ValueError("Neither DATABASE_URL nor full set of DB components (USERNAME, PASSWORD, HOSTNAME, DATABASE) found in environment variables")

# Mask password for logging
masked_url = db_url
if "@" in db_url:
    try:
        # Extract host and database name, mask username and password
        parts = db_url.split("@")
        masked_url = f"***@{parts[1]}"
    except Exception:
        masked_url = "URL Masking Error"

print(f"Connecting to database at: {masked_url}")

# Fix for Render/Heroku: update URLs starting with postgres:// to postgresql://
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    db_url, 
    connect_args={"connect_timeout": 10},
    pool_pre_ping=True,
    pool_recycle=3600
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
