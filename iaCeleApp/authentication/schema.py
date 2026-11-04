from typing import Optional
from datetime import datetime, timezone
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from sqlmodel.main import NaiveDatetime

from .crud import password_hash


class TipoUsuario(str, Enum):
    empleado = "empleado"
    accionista = "accionista"
    cliente = "cliente"
    proveedor = "proveedor"


class AuthenticationsBase(SQLModel):
    username: str = Field(unique=True, index=True)


class AuthenticationsCreate(AuthenticationsBase):
    tipo: TipoUsuario
    empleado_id: int|None
    avatar: str|None = None


class Authentications(AuthenticationsBase, table=True):
    id: int|None = Field(default=None, primary_key=True)
    avatar: str|None = None
    password_hashed: str
    fecha_alta: NaiveDatetime = Field(default_factory=datetime.now)
    tipo: TipoUsuario
    
    empleado_id: int|None = Field(foreign_key="employees.id", unique=True)
    empleado: Optional["Employees"] = Relationship(
        back_populates="app_user",
        sa_relationship_kwargs={
            "uselist": False,
            "foreign_keys": "Authentications.empleado_id",
            "lazy": "joined"
        }
    )

    # Verifica de forma segura si la contraseña coincide con el hash de la DB
    def verify_password(self, password_str: str) -> bool:
        return password_hash.verify(password_str, self.password_hashed)


class AuthenticationsUpdate(SQLModel):
    avatar: str|None = None
    password_str: str|None = None


class Token(SQLModel):
    access_token: str
    token_type: str
