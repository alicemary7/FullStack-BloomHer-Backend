from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from datetime import datetime
from db.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    price = Column(Float, nullable=False) # Base price or default price
    price_small = Column(Float, nullable=True)
    price_regular = Column(Float, nullable=True)
    price_large = Column(Float, nullable=True)
    price_xl = Column(Float, nullable=True)
    rating = Column(Float, default=0)
    review_count = Column(Integer, default=0)
    description = Column(Text)
    image_url = Column(Text)
    features = Column(Text) # Comma-separated or newline-separated features
    
    # Keeping existing fields to ensure app stability
    
    stock = Column(Integer, nullable=False)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
