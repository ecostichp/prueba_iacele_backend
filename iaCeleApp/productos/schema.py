from sqlmodel import SQLModel, Field
from datetime import datetime, timezone


class ProductsBase(SQLModel):
    id_odoo: int = Field(unique=True, index=True)
    code: str = Field(unique=True)
    name: str = Field(unique=True, index=True, default='Nuevo producto')
    cost: float = 0
    price: float = 0


class ProductsCreate(ProductsBase):
    pass


class Products(ProductsBase, table=True):

    id: int|None = Field(default=None, primary_key=True)
    fecha_alta: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProductsUpdate(SQLModel):
    name: str | None = None
    cost: float | None = None
    price: float | None = None
