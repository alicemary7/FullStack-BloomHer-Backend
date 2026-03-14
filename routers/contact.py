from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from dependencies import connect_db
from models.contact import Contact
from schemas.contact import ContactCreate, ContactOut
from typing import List
from routers.users import get_current_user
from models.users import User

contact_router = APIRouter(prefix="/contacts", tags=["Contacts"])

@contact_router.post("/", status_code=status.HTTP_201_CREATED, response_model=ContactOut)
def create_contact(
    data: ContactCreate,
    db: Session = Depends(connect_db)
):
    try:
        new_contact = Contact(
            name=data.name,
            email=data.email,
            subject=data.subject,
            message=data.message
        )
        db.add(new_contact)
        db.commit()
        db.refresh(new_contact)
        return new_contact
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@contact_router.get("/", response_model=List[ContactOut])
def get_contacts(
    db: Session = Depends(connect_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    return db.query(Contact).all()
