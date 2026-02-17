from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from dependencies import connect_db
from models.order import Order
from models.product import Product
from schemas.order import OrderCreate, OrderOut
from routers.users import get_current_user
from models.users import User

order_router = APIRouter(prefix="/orders", tags=["Orders"])

# Separate function to calculate price based on size (10% increments)
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

    shipping_fee = 0
    # Use the new calculation function to determine price based on size
    price = calculate_price_by_size(product.price, order_data.size)

    total_amount = (price * order_data.quantity) + shipping_fee



    order = Order(
        user_id=user_id,
        product_id=order_data.product_id,
        quantity=order_data.quantity,
        size=order_data.size,
        total_amount=total_amount,
        status="processing"
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
    # Check if the logged-in user has the "admin" role
    if current_user.role != "admin":
        # If not an admin, return a 403 Forbidden error (security barrier)
        raise HTTPException(status_code=403, detail="Only admins can view all orders")
    
    # If admin check passes, query all orders recorded in the database
    return db.query(Order).all()


@order_router.get("/user/{user_id}", response_model=List[OrderOut])
def get_user_orders(
    user_id: int, 
    db: Session = Depends(connect_db),
    current_user: User = Depends(get_current_user)
):
    orders = db.query(Order).filter(Order.user_id == user_id).all()
    return orders


from sqlalchemy.orm import Session, joinedload

@order_router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int, 
    db: Session = Depends(connect_db),
    current_user: User = Depends(get_current_user)
):
    order = db.query(Order).options(joinedload(Order.product)).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if the order belongs to the user or if the user is admin
    if order.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You are not authorized to view this order")
        
    return order


@order_router.patch("/{order_id}/status")
def update_order_status(
    order_id: int,
    new_status: str,
    db: Session = Depends(connect_db),
    current_user: User = Depends(get_current_user)
):
    # Ensure only users with the "admin" role can change order statuses
    if current_user.role != "admin":
        # If not admin, block the update and return 403 Forbidden
        raise HTTPException(status_code=403, detail="Only admins can update order status")
   
    # Search for the specific order by its unique ID
    order = db.query(Order).filter(Order.id == order_id).first()
    
    # If the order ID doesn't exist, return a 404 Not Found error
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Update the status field with the new value provided in the request
    order.status = new_status
    # Save the changes to the database
    db.commit()
    # Refresh the order object with the latest data from the database
    db.refresh(order)
    # Return the updated order details
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
