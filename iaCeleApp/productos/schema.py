from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ProductosBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    codigo: int
    descripcion: str
    linea: str
    existencia: float = 0
    ultimo_costo: float = 0
    cantidad_ventas_anuales: float = 0
    monto_ventas_anuales: float = 0



class ProductosCreate(ProductosBase):
    fecha_ultima_compra_str: str
    fecha_ultima_venta_str: str


class Productos(ProductosBase):
    id: int
    estatus: bool = True
    fecha_ultima_compra: datetime | None
    fecha_ultima_venta: datetime | None
