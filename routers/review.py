from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies import connect_db
from models.review import Review
from models.product import Product
from models.users import User
from schemas.review import ReviewCreate, ReviewOut, ReviewDelete
from routers.users import get_current_user

review_router = APIRouter(prefix="/reviews", tags=["Reviews"])


@review_router.post("/", status_code=status.HTTP_201_CREATED)
def create_review(
    data: ReviewCreate,
    db: Session = Depends(connect_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    review = Review(
        user_id=current_user.id,            
        product_id=data.product_id,
        rating=data.rating,
        comment=data.comment,
    )

    db.add(review)
    
    # Update Product Rating & Count
    reviews = db.query(Review).filter(Review.product_id == data.product_id).all()
    all_ratings = [r.rating for r in reviews] + [data.rating]
    product.review_count = len(all_ratings)
    product.rating = sum(all_ratings) / len(all_ratings)

    db.commit()
    db.refresh(review)

    return review



@review_router.get("/product/{product_id}")
def get_product_reviews(product_id: int, db: Session = Depends(connect_db)):
    return db.query(Review).filter(Review.product_id == product_id).all()


@review_router.get("/user/{user_id}")
def get_user_reviews(user_id: int, db: Session = Depends(connect_db)):
    return db.query(Review).filter(Review.user_id == user_id).all()


@review_router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int, 
    db: Session = Depends(connect_db),
    current_user: User = Depends(get_current_user)
):
    review = db.query(Review).filter(Review.id == review_id).first()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    if review.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this review")

    db.delete(review)

    # Update Product Rating & Count
    product = db.query(Product).filter(Product.id == review.product_id).first()
    remaining_reviews = db.query(Review).filter(Review.product_id == review.product_id, Review.id != review_id).all()
    if remaining_reviews:
        all_ratings = [r.rating for r in remaining_reviews]
        product.review_count = len(all_ratings)
        product.rating = sum(all_ratings) / len(all_ratings)
    else:
        product.review_count = 0
        product.rating = 0

    db.commit()

    return {"message": "Review deleted"}

