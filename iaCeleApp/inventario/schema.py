from typing import Optional
from datetime import datetime
from enum import Enum
from pydantic import field_serializer
from sqlmodel import SQLModel, Field, Relationship

from ..timeutil import as_utc, utc_now


class TipoConteo(str, Enum):
    gerente = "gerente"
    doble = "doble"
    equipo = "equipo"
    individual = "individual"


class InventoryBase(SQLModel):
    id_products: int = Field(foreign_key="products.id")
    count_qty: float
    assigned_team_id: int = Field(foreign_key="teams.id")
    assigned_user_id: int | None = Field(default=None, foreign_key="employees.id")
    counting_user_id: int = Field(foreign_key="employees.id")
    count_type: TipoConteo


class InventoryCreate(InventoryBase):
    pass


class Inventory(InventoryBase, table=True):
    id: int|None = Field(default=None, primary_key=True)
    date_create: datetime | None = Field(default_factory=utc_now)

    @field_serializer("date_create")
    def serialize_date_create(self, value):
        converted = as_utc(value)
        return None if converted is None else converted.isoformat()
    assigned_user_team: Optional["Teams"] | None = Relationship(
        sa_relationship_kwargs={
        "uselist": False,
        "foreign_keys": "[Inventory.assigned_team_id]",
        }
    )
    assigned_user_employee: Optional["Employees"] | None = Relationship(
        sa_relationship_kwargs={
        "uselist": False,
        "foreign_keys": "[Inventory.assigned_user_id]",
        }
    )
    counting_user_employee: Optional["Employees"] | None = Relationship(
        sa_relationship_kwargs={
        "uselist": False,
        "foreign_keys": "[Inventory.counting_user_id]",
        }
    )


class Inventory_InvididualRegisters(SQLModel):
    id_products: int
    code: str
    name: str
    total_qty: float
    last_count: datetime | None = None

    @field_serializer("last_count")
    def serialize_last_count(self, value):
        converted = as_utc(value)
        return None if converted is None else converted.isoformat()


class Inventory_InvididualProductAllRegisters(SQLModel):
    product_id: dict
    registers: list[dict]


class InventoryStage(SQLModel, table=True):
    __tablename__ = "inventory_stage"
    id: int | None = Field(default=None, primary_key=True)
    stage: TipoConteo = TipoConteo.individual


class InventoryStagePublic(SQLModel):
    stage: TipoConteo


class Inventory_TeamRegisters(SQLModel):
    id_products: int
    code: str
    name: str
    total_qty_a: float | None
    total_qty_b: float | None
    total_qty_equipo: float | None = None
    iguales: bool
    