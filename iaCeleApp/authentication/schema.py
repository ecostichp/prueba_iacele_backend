from pydantic import BaseModel, ConfigDict



class AuthBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user: str
    name: str
    position: str
    avatar: str


class AuthCreate(AuthBase):
    password: str


class Auth(AuthBase):
    id: int
    hashed_password: str
