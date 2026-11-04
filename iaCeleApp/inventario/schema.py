from typing import Optional
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from sqlmodel.main import NaiveDatetime
from datetime import datetime


class TipoConteo(str, Enum):
    gerente = "gerente"
    doble = "doble"
    equipo = "equipo"
    individual = "individual"


class InventoryBase(SQLModel):
    id_products: int = Field(foreign_key="products.id")
    count_qty: float
    assigned_team_id: int = Field(foreign_key="teams.id")
    assigned_user_id: int = Field(foreign_key="employees.id")
    counting_user_id: int = Field(foreign_key="employees.id")
    count_type: TipoConteo


class InventoryCreate(InventoryBase):
    pass


class Inventory(InventoryBase, table=True):
    id: int|None = Field(default=None, primary_key=True)
    date_create: NaiveDatetime  = Field(default_factory=datetime.now)
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

class Inventory_TeamRegisters(SQLModel):
    id_products: int
    code: str
    name: str
    total_qty: float