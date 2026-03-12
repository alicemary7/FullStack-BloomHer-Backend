from passlib.context import CryptContext

# passlib is a password hashing library.
# jose is a jwt library
from jose import JWTError, jwt

from datetime import datetime, timedelta
from core.config import SECRET_KEY, ALGORITHM

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# password verify function(login)

def verify_password(plain_password, hashed_password):
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Fallback for legacy plain-text passwords stored in the database
        return plain_password == hashed_password


# password hash function(signup)

def get_password_hash(password):
    return pwd_context.hash(password)

# jwt token creation function(after login)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
