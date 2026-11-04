from typing import Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship
from sqlmodel.main import NaiveDatetime


class EmployeesBase(SQLModel):
    id_odoo: int = Field(unique=True, index=True)
    name: str = Field(unique=True, index=True)
    job_title: str
    department: str
    warehouse: str


class EmployeesCreate(EmployeesBase):
    hire_date_str: str


class Employees(EmployeesBase, table=True):

    id: int|None = Field(default=None, primary_key=True)
    hire_date: NaiveDatetime
    active: bool = True
    create_date: NaiveDatetime = Field(default_factory=datetime.now)
    is_app_user: bool = False
    app_user: Optional["Authentications"] = Relationship(
        back_populates="empleado",
        sa_relationship_kwargs={
            "uselist": False,
            "foreign_keys": "Authentications.empleado_id",
            "lazy": "joined"
        }
    )
    team_a: Optional["Teams"] = Relationship(
        back_populates="empleado_a",
        sa_relationship_kwargs={
            "uselist": False,
            "foreign_keys": "Teams.empleado_id_a",
            "lazy": "joined"
        }
    )
    team_b: Optional["Teams"] = Relationship(
        back_populates="empleado_b",
        sa_relationship_kwargs={
            "uselist": False,
            "foreign_keys": "Teams.empleado_id_b",
            "lazy": "joined"
        }
    )


class EmployeesUpdate(SQLModel):
    name: str | None = None
    job_title: str | None = None
    hire_date_str: str | None = None
    department: str | None = None
    warehouse: str | None = None
    active: bool | None = None


class EmployeesAuthentication(SQLModel):
    is_app_user: bool
    username: str
    avatar: str | None = None
    tipo: str = 'empleado'
