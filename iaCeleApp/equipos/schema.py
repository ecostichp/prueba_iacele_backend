from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship, CheckConstraint

from ..timeutil import utc_now


class TeamsBase(SQLModel):
    empleado_id_a: int|None = Field(foreign_key="employees.id", unique=True)
    empleado_id_b: int|None = Field(foreign_key="employees.id", unique=True)


class TeamsCreate(TeamsBase):
    pass


class Teams(TeamsBase, table=True):

    __table_args__ = (
        CheckConstraint("empleado_id_a != empleado_id_b", name="check_empleados_a_b_únicos_en_equipo"),
    )

    id: int|None = Field(default=None, primary_key=True)
    create_date: datetime | None = Field(default_factory=utc_now)
    
    empleado_a: Optional["Employees"] = Relationship(
        sa_relationship_kwargs={
            "uselist": False,
            "foreign_keys": "Teams.empleado_id_a",
            "lazy": "joined"
        }
    )
    empleado_b: Optional["Employees"] = Relationship(
        sa_relationship_kwargs={
            "uselist": False,
            "foreign_keys": "Teams.empleado_id_b",
            "lazy": "joined"
        }
    )


class TeamsUpdate(SQLModel):
    empleado_id_a: int | None = None
    empleado_id_b: int | None = None
