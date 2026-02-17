from sqlalchemy import Column, Integer, String, Boolean
from db.database import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password = Column(String(100), nullable=False)

    role = Column(String(20), default="user")   
    is_active = Column(Boolean, default=True)

    carts = relationship("Cart", back_populates="user")
