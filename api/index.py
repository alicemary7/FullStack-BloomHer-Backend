from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from db.database import Base, engine
from models import (
    Product,
    User, Cart, Order, Payment, Review
)
from routers.product import router as product_router
from routers.users import user_router
from routers.cart import cart_router
from routers.order import order_router
from routers.review import review_router
from routers.payment import payment_router

app = FastAPI(title="BloomHer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    print("Connecting to database...")
    try:
        # Tables creation
        try:
            Base.metadata.create_all(bind=engine)
            print("Tables created successfully.")
        except Exception as e:
            print(f"Error creating tables: {e}")

        # Schema updates
        try:
            with engine.connect() as conn:
                print("Checking for missing columns...")
                # Add missing columns if they don't exist
                conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS price_small FLOAT"))
                conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS price_regular FLOAT"))
                conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS price_large FLOAT"))
                conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS price_xl FLOAT"))
                conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS rating FLOAT DEFAULT 0"))
                conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS review_count INTEGER DEFAULT 0"))
                conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS features TEXT"))
                conn.commit()
                print("Schema update check completed.")
        except Exception as e:
            print(f"Error updating schema: {e}")
            
    except Exception as general_e:
        print(f"General startup error (backend will still try to run): {general_e}")

@app.get("/")
def home():
    return {
        "message": "BloomHer backend is running",
        "status": "online",
        "docs": "/docs",
        "debug": "/debug-routes"
    }

@app.get("/debug-routes")
def debug_routes():
    return [{"path": route.path, "name": route.name} for route in app.routes]

# Include routers
app.include_router(product_router)
app.include_router(user_router)
app.include_router(cart_router)
app.include_router(order_router)
app.include_router(review_router)
# Alias for Vercel/Serverless deployment
handler = app
