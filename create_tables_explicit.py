from db.database import Base, engine
from models import Product, User, Cart, Order, Payment, Review

def create_tables():
    print("Creating tables for all models...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Done! Check your pgAdmin for the following tables:")
        print(Base.metadata.tables.keys())
    except Exception as e:
        print(f"Error during table creation: {e}")

if __name__ == "__main__":
    create_tables()
