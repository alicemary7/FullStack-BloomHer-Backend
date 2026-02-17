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

app=FastAPI()

@app.on_event("startup")
def on_startup():
    print("Connecting to database...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")

    with engine.connect() as conn:
        print("Checking for missing columns...")
        try:
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:5501",
        "http://127.0.0.1:5501",
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def greet():
    return {"message": "Welcome to server. Visit /docs for API documentation."}

@app.get("/debug-routes")
def debug_routes():
    return [{"path": route.path, "name": route.name} for route in app.routes]

app.include_router(product_router)
app.include_router(user_router)
app.include_router(cart_router)
app.include_router(order_router)
app.include_router(review_router)
app.include_router(payment_router)
