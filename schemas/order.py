from pydantic import BaseModel
from typing import Optional
from datetime import datetime


from schemas.product import ProductOut
from schemas.users import UserShow

class OrderCreate(BaseModel):
    product_id: int
    quantity: int
    size: Optional[str] = "Regular"

class OrderOut(BaseModel):
    id: int 
    user_id: int
    product_id: int
    quantity: int
    size: Optional[str] = "Regular"
    total_amount: float
    status: str  
    order_date: datetime
    product: Optional[ProductOut] = None
    user: Optional[UserShow] = None

    model_config = {"from_attributes": True}
