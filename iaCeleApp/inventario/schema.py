from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from sqlmodel.main import NaiveDatetime
from datetime import datetime



class Inventory_individualBase(SQLModel):
    id_products: int = Field(foreign_key="products.id")
    count_qty: float
    assigned_team_id: int = Field(foreign_key="teams.id")
    assigned_user_id: int = Field(foreign_key="employees.id")
    counting_user_id: int = Field(foreign_key="employees.id")

class Inventory_individualCreate(Inventory_individualBase):
    pass

class Inventory_individual(Inventory_individualBase, table=True):
    id: int|None = Field(default=None, primary_key=True)
    date_create: NaiveDatetime  = Field(default_factory=datetime.now)
    assigned_user_team: Optional["Teams"] | None = Relationship(
        sa_relationship_kwargs={
        "uselist": False,
        "foreign_keys": "[Inventory_individual.assigned_team_id]",
        }
    )
    assigned_user_employee: Optional["Employees"] | None = Relationship(
        sa_relationship_kwargs={
        "uselist": False,
        "foreign_keys": "[Inventory_individual.assigned_user_id]",
        }
    )
    counting_user_employee: Optional["Employees"] | None = Relationship(
        sa_relationship_kwargs={
        "uselist": False,
        "foreign_keys": "[Inventory_individual.counting_user_id]",
        }
    )

class Inventory_individualUpdate(SQLModel):
    count_qty: float | None = None
