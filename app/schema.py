from pydantic import BaseModel, ConfigDict

from datetime import datetime



class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user: str
    name: str
    position: str
    avatar: str

class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    hashed_password: str

        