from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.product import router as product_router
from routers.users import user_router
from routers.cart import cart_router
from routers.order import order_router
from routers.review import review_router
from routers.payment import payment_router
from routers.contact import contact_router
app = FastAPI(title="BloomHer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://full-stack-bloom-her-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
app.include_router(payment_router)
app.include_router(contact_router)
