from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from dependencies import connect_db
from models.order import Order
from models.product import Product
from schemas.order import OrderCreate, OrderOut
from routers.users import get_current_user
from models.users import User

order_router = APIRouter(prefix="/orders", tags=["Orders"])

def calculate_price_by_size(base_price: float, size: str) -> float:
    multiplier = 1.0
    if size == "Small": multiplier = 0.9
    elif size == "Regular": multiplier = 1.0
    elif size == "Large": multiplier = 1.1
    elif size == "XL": multiplier = 1.2
    
    return round(base_price * multiplier)

@order_router.post("/", status_code=status.HTTP_201_CREATED, response_model=OrderOut)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(connect_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id
    
    product = db.query(Product).filter(Product.id == order_data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if order_data.quantity >= 99:
        order_data.quantity = 98

    # Check stock
    if product.stock < order_data.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock available")

    # Deduct stock
    product.stock -= order_data.quantity
    db.add(product) # Explicitly mark this as updated for safety

    shipping_fee = 0
    price = calculate_price_by_size(product.price, order_data.size)

    total_amount = (price * order_data.quantity) + shipping_fee

    order = Order(
        user_id=user_id,
        product_id=order_data.product_id,
        quantity=order_data.quantity,
        size=order_data.size,
        total_amount=total_amount,
        status="processing",
        email=order_data.email,
        phone_number=order_data.phone_number,
        shipping_address=order_data.shipping_address
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@order_router.get("/", response_model=List[OrderOut])
def get_all_orders(
    db: Session = Depends(connect_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view all orders")
    
    return db.query(Order).options(joinedload(Order.product)).all()


@order_router.get("/user/{user_id}", response_model=List[OrderOut])
def get_user_orders(
    user_id: int, 
    db: Session = Depends(connect_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You are not authorized to view these orders")
        
    orders = db.query(Order).options(joinedload(Order.product)).filter(Order.user_id == user_id).all()
    return orders


@order_router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int, 
    db: Session = Depends(connect_db),
    current_user: User = Depends(get_current_user)
):
    order = db.query(Order).options(joinedload(Order.product)).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You are not authorized to view this order")
        
    return order


@order_router.patch("/{order_id}/status")
def update_order_status(
    order_id: int,
    new_status: str,
    cancel_reason: str = None,
    db: Session = Depends(connect_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update order status")
   
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Restore stock if the order is being cancelled
    if new_status == "cancelled" and order.status != "cancelled":
        product = db.query(Product).filter(Product.id == order.product_id).first()
        if product:
            product.stock += order.quantity
            
    # Deduct stock if order is being un-cancelled
    elif new_status != "cancelled" and order.status == "cancelled":
        product = db.query(Product).filter(Product.id == order.product_id).first()
        if product:
            if product.stock < order.quantity:
                raise HTTPException(status_code=400, detail="Not enough stock available to un-cancel this order")
            product.stock -= order.quantity
            
    order.status = new_status
    if new_status == "cancelled" and cancel_reason:
        order.cancel_reason = cancel_reason
        
    db.commit()
    db.refresh(order)
    return order


@order_router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(
    order_id: int, 
    db: Session = Depends(connect_db),
    current_user: User = Depends(get_current_user)
):
  
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    db.delete(order)
    db.commit()
    return {"message":"deleted successfully"}

