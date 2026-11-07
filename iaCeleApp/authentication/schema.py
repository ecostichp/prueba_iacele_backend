from typing import Optional
from enum import Enum
from datetime import datetime
from pydantic import model_validator
from sqlmodel import SQLModel, Field, Relationship

from ..timeutil import utc_now
from .crud import password_hash


class TipoUsuario(str, Enum):
    empleado = "empleado"
    accionista = "accionista"
    cliente = "cliente"
    proveedor = "proveedor"


class AuthenticationsBase(SQLModel):
    username: str = Field(unique=True, index=True)
    counting_user_id: int|None
    assigned_user_id: int|None
    tipo: TipoUsuario
    empleado_id: int|None = Field(foreign_key="employees.id", unique=True)


class AuthenticationsCreate(AuthenticationsBase):
    avatar: str | None = None
    counting_user_id: int | None = None
    assigned_user_id: int | None = None

    @model_validator(mode="after")
    def set_user_ids_from_empleado(self):
        self.counting_user_id = self.empleado_id
        self.assigned_user_id = self.empleado_id
        return self

class Authentications(AuthenticationsBase, table=True):
    id: int|None = Field(default=None, primary_key=True)
    avatar: str|None = None
    password_hashed: str
    fecha_alta: datetime | None = Field(default_factory=utc_now)
    
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

class AuthenticationsPublic(SQLModel):
    username: str
    avatar: str|None
    empleado_id: int|None
    counting_user_id: int|None
    assigned_user_id: int|None
    tipo: str 

class Token(SQLModel):
    access_token: str
    token_type: str


class AppAccess(SQLModel, table=True):
    __tablename__ = "app_access"
    id: int | None = Field(default=None, primary_key=True)
    login_open: bool = True
    tokens_valid_after: datetime | None = None


class AccessState(SQLModel):
    login_open: bool


class UserAssignment(SQLModel):
    empleado_id: int
    assigned_user_id: int


class UserAssignmentBatch(SQLModel):
    items: list[UserAssignment]


class AssignmentNotice(SQLModel, table=True):
    __tablename__ = "assignment_notices"
    id: int | None = Field(default=None, primary_key=True)
    empleado_id: int = Field(index=True)
    assigned_user_id: int
    message: str
    seen: bool = False
    fecha_alta: datetime | None = Field(default_factory=utc_now)


class AssignmentNoticePublic(SQLModel):
    id: int
    assigned_user_id: int
    message: str


class DataRepair(SQLModel, table=True):
    __tablename__ = "data_repairs"
    id: str = Field(primary_key=True)
    applied_at: datetime | None = Field(default_factory=utc_now)
