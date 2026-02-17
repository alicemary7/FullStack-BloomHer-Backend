from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from dependencies import connect_db
from models import Product
from schemas.product import ProductCreate
from routers.users import get_current_user
from models.users import User

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_product(
    data: ProductCreate, 
    db: Session = Depends(connect_db),
    current_user: User = Depends(get_current_user)
):
    # Only admins can create
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    
    try:
        # Use exclude_unset=True to only include fields provided in the request
        # This prevents errors if the DB table is missing columns for optional fields
        product_data = data.model_dump(exclude_unset=True)
        product = Product(**product_data)
        db.add(product)
        db.commit()
        db.refresh(product)
        return product
    except Exception as e:
        db.rollback()
        print(f"Error creating product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Database error: {str(e)}"
        )


@router.get("/")
def get_products(db: Session = Depends(connect_db)):
    return db.query(Product).filter(Product.is_active == True).all()


@router.get("/{product_id}")
def get_single_product(
    product_id: int, db: Session = Depends(connect_db)
):
    single_product = db.query(Product).filter(Product.id == product_id).first()
    if not single_product:
        raise HTTPException(status_code=404, detail="product not found")
    return single_product


@router.put("/{product_id}")
def update_product(
    product_id: int, 
    data: ProductCreate, 
    db: Session = Depends(connect_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
        
    target_product = db.query(Product).filter(Product.id == product_id).first()
    if not target_product:
        raise HTTPException(status_code=404, detail="product not found")
    
    try:
        # Get only the data that was sent in the request
        update_data = data.model_dump(exclude_unset=True)
        
        # Update each field in the existing product object
        for key, value in update_data.items():
            setattr(target_product, key, value)
            
        db.commit()
        db.refresh(target_product)
        return target_product
    except Exception as e:
        db.rollback()
        print(f"Error updating product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Database error: {str(e)}"
        )


@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
def delete_product(
    product_id: int, 
    db: Session = Depends(connect_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="product not found")
    
    product.is_active = False
    db.commit()
    return {"message": "Product deactivated successfully"}
