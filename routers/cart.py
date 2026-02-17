from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from models.cart import Cart
from schemas.cart import CartOut, CartCreate
from dependencies import connect_db
from routers.users import get_current_user
from models.users import User

cart_router = APIRouter(prefix="/cart", tags=["Cart"])

@cart_router.get("/", response_model=List[CartOut])
def get_cart(db: Session = Depends(connect_db), current_user: User = Depends(get_current_user)):
    cart_items = db.query(Cart).filter(Cart.user_id == current_user.id).all()
    return cart_items

@cart_router.post("/", status_code=status.HTTP_201_CREATED, response_model=CartOut)
def add_to_cart(cart_data: CartCreate, db: Session = Depends(connect_db), current_user: User = Depends(get_current_user)):
    user_id = current_user.id

    existing_item = db.query(Cart).filter(
        Cart.user_id == user_id, 
        Cart.product_id == cart_data.product_id,
        Cart.size == cart_data.size
    ).first()

    if cart_data.quantity >= 99:
        cart_data.quantity = 98

    if existing_item:
        existing_item.quantity += cart_data.quantity
        if existing_item.quantity >= 99:
            existing_item.quantity = 98
        db.commit()
        db.refresh(existing_item)
        return existing_item
    
    new_cart_item = Cart(
        user_id=user_id,
        product_id=cart_data.product_id,
        quantity=cart_data.quantity,
        size=cart_data.size
    )
    db.add(new_cart_item)
    db.commit()
    db.refresh(new_cart_item)
    return new_cart_item



@cart_router.delete("/item/{product_id}")
def remove_cart_item(product_id: int, db: Session = Depends(connect_db), current_user: User = Depends(get_current_user)):
    item = db.query(Cart).filter(Cart.user_id == current_user.id, Cart.product_id == product_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    
    db.delete(item)
    db.commit()
    return {"message": "Item removed from cart"}

@cart_router.put("/item/{product_id}")
def update_cart_item_quantity(
    product_id: int, 
    quantity: int, 
    db: Session = Depends(connect_db),
    current_user: User = Depends(get_current_user)
):
    item = db.query(Cart).filter(Cart.user_id == current_user.id, Cart.product_id == product_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    
    if quantity <= 0:
        db.delete(item)
        db.commit()
        return {"message": "Item removed"}
        
    if quantity >= 99:
        quantity = 98
        
    item.quantity = quantity
    db.commit()
    db.refresh(item)
    return item




