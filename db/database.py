import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
load_dotenv()

# Get DB URL from environment variables for Render deployment
# Fallback to the hardcoded URL for local testing if needed
db_url = os.environ.get("DATABASE_URL")
if not db_url:
    # Local PostgreSQL connection string
    # db_url = "postgresql://postgres:AcademyRootPassword@localhost:5432/fullstack_bloomher"
    db_url = "postgresql://e_commerce_cfl6_user:yHRmBPVWDe4romHRpvOLI5aOfKNzKgJ0@dpg-d6ighv15pdvs73e3f7ng-a.oregon-postgres.render.com/e_commerce_cfl6"

# Mask password for logging
masked_url = db_url
if "@" in db_url:
    try:
        # Extract host and database name, mask username and password
        parts = db_url.split("@")
        masked_url = parts[1]
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
