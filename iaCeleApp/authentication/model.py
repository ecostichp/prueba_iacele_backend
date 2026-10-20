from sqlalchemy import Column, Integer, String
from pwdlib import PasswordHash

from ..database import Base


# Inicializamos el mismo verificador
password_hash = PasswordHash.recommended()

class Auth(Base):
    __tablename__ = 'authentication'

    id = Column(Integer, primary_key=True, index=True)
    user = Column(String(16,), nullable=False, unique=True, index=True)
    name = Column(String(64,), nullable=False, index=True)
    position = Column(String(64,), nullable=False, index=True)
    avatar = Column(String(16,), nullable=False, index=True)
    hashed_password = Column(String(124,), nullable=False, index=True)

    def verify_password(self, password: str) -> bool:
        # Verifica de forma segura si la contraseña coincide con el hash de la BD
        return password_hash.verify(password, self.hashed_password)