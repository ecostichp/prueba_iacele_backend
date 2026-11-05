from typing import Optional
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship, func
from sqlmodel.main import NaiveDatetime


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
    date_create: NaiveDatetime|None = Field(default=None, sa_column_kwargs={"server_default": func.now()})
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


class Inventory_InvididualProductAllRegisters(SQLModel):
    product_id: dict
    registers: list[dict]


class Inventory_TeamRegisters(SQLModel):
    id_products: int
    code: str
    name: str
    total_qty_a: float | None
    total_qty_b: float | None
    iguales: bool
    