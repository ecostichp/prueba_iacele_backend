from sqlalchemy import Column, Integer, String
from passlib.hash import bcrypt

from .orm import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    user = Column(String(16,), nullable=False, unique=True, index=True)
    name = Column(String(64,), nullable=False, index=True)
    position = Column(String(64,), nullable=False, index=True)
    avatar = Column(String(16,), nullable=False, index=True)
    hashed_password = Column(String(124,), nullable=False, index=True)

    def verify_password(self, password: str):
        return bcrypt.verify(password, self.hashed_password)
