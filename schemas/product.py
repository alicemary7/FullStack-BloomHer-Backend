from pydantic import BaseModel
from typing import List, Optional, Any

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    price_small: Optional[float] = None
    price_regular: Optional[float] = None
    price_large: Optional[float] = None
    price_xl: Optional[float] = None
    rating: Optional[float] = 0
    stock: int
    image_url: str
    features: Optional[str] = ""
    review_count: Optional[int] = 0


class ProductOut(ProductCreate):
    id: int
    is_active: bool

    model_config = {"from_attributes": True}


