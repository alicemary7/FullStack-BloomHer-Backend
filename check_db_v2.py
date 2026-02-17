import sqlalchemy
from sqlalchemy import create_engine, text

def check_db():
    # Try to connect to postgres default database to check if server is up
    url = "postgresql://postgres:AcademyRootPassword@localhost:5432/postgres"
    engine = create_engine(url)
    try:
        with engine.connect() as conn:
            print("Successfully connected to PostgreSQL server!")
            
            # Check if Trail_db exists
            result = conn.execute(text("SELECT 1 FROM pg_database WHERE datname='Trail_db'"))
            exists = result.fetchone()
            if not exists:
                print("Database 'Trail_db' does not exist. Creating it...")
                conn.execute(text("COMMIT")) # End current transaction
                conn.execute(text("CREATE DATABASE \"Trail_db\""))
                print("Database 'Trail_db' created successfully.")
            else:
                print("Database 'Trail_db' already exists.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_db()
