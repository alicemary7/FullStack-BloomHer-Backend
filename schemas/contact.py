from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ContactCreate(BaseModel):
    name: str
    email: str
    subject: str
    message: str

class ContactOut(ContactCreate):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
