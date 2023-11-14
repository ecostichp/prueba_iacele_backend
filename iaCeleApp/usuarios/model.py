from sqlalchemy import Boolean, Column, Integer, SmallInteger, String, DateTime
from datetime import datetime

from ..database import Base


class Usuarios(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    usuario = Column(String(16,), nullable=False, unique=True, index=True)
    estatus = Column(Boolean, nullable=False, default=True)
    nombre_1ro = Column(String(16,), nullable=False)
    nombre_2do = Column(String(16,), )
    apellido_paterno = Column(String(16,), nullable=False)
    apellido_materno = Column(String(16,), nullable=False)
    almacen = Column(SmallInteger, nullable=False)
    fecha_nacimiento = Column(DateTime, nullable=False)
    fecha_alta = Column(DateTime, nullable=False, default=datetime.now())
    avatar = Column(String(16,), default="no-avatar")