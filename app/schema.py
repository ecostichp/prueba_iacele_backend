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
        