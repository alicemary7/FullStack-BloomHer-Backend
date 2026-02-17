from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies import connect_db
from models.review import Review
from models.product import Product
# Import the User model to handle user data
from models.users import User
from schemas.review import ReviewCreate, ReviewOut, ReviewDelete
# Import get_current_user to identify who is making the request via their token
from routers.users import get_current_user

review_router = APIRouter(prefix="/reviews", tags=["Reviews"])


# Handle POST requests to create a new review
@review_router.post("/", status_code=status.HTTP_201_CREATED)
def create_review(
    data: ReviewCreate,
    db: Session = Depends(connect_db),
    # Identify the user automatically from their login token
    current_user: User = Depends(get_current_user)
):
    # Check if the product being reviewed actually exists
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        # If product is not found, return 404 error
        raise HTTPException(status_code=404, detail="Product not found")

    # Create a new Review entry in the database
    review = Review(
        # Use the ID of the logged-in user (from token) for security
        user_id=current_user.id,            
        product_id=data.product_id,
        rating=data.rating,
        comment=data.comment,
    )

    # Add the review to the database session
    db.add(review)
    # Commit (save) the changes to the database
    db.commit()
    # Refresh the object to get updated data (like generated ID)
    db.refresh(review)

    # Return the newly created review
    return review



@review_router.get("/product/{product_id}")
def get_product_reviews(product_id: int, db: Session = Depends(connect_db)):
    return db.query(Review).filter(Review.product_id == product_id).all()


@review_router.get("/user/{user_id}")
def get_user_reviews(user_id: int, db: Session = Depends(connect_db)):
    return db.query(Review).filter(Review.user_id == user_id).all()


# Handle DELETE requests to remove a review
@review_router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int, 
    db: Session = Depends(connect_db),
    # Get the details of the user trying to delete the review
    current_user: User = Depends(get_current_user)
):
    # Search for the review in the database by ID
    review = db.query(Review).filter(Review.id == review_id).first()

    # If the review doesn't exist, return a 404 error
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Permission check: Allow deletion ONLY if the logged-in user is the owner OR is an admin
    if review.user_id != current_user.id and current_user.role != "admin":
        # If neither, block the request with a 403 error
        raise HTTPException(status_code=403, detail="Not authorized to delete this review")

    # If authorized, delete the review from the database session
    db.delete(review)
    # Commit the deletion to the database
    db.commit()

    # Return a success message
    return {"message": "Review deleted"}
