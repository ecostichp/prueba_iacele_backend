from sqlalchemy import Boolean, Column, Integer, String, Float, DateTime

from ..database import Base


class Productos(Base):
    __tablename__ = "productos"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(Integer, nullable=False, unique=True, index=True)
    descripcion = Column(String(128,), nullable=False)
    estatus = Column(Boolean, nullable=False, default=True)
    linea = Column(String(16,), nullable=False)
    fecha_ultima_compra = Column(DateTime, )
    fecha_ultima_venta = Column(DateTime, )
    existencia = Column(Float, nullable=False, default=0)
    ultimo_costo = Column(Float, nullable=False, default=0)
    cantidad_ventas_anuales = Column(Float, nullable=False, default=0)
    monto_ventas_anuales = Column(Float, nullable=False, default=0)
