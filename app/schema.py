from pydantic import BaseModel

from datetime import datetime



class UserBase(BaseModel):
    user: str
    name: str
    position: str
    avatar: str

class UserCreate(UserBase):
    password: str

    class Config:
        orm_mode = True

class User(UserBase):
    id: int
    hashed_password: str

    class Config:
        orm_mode = True



class LeadBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    company: str
    note: str

class LeadCreate(LeadBase):
    pass

class Lead(LeadBase):
    id: int
    owner_id: int
    date_created: datetime
    date_last_updated: datetime

    class Config:
        orm_mode = True