from pydantic import BaseModel, ConfigDict
from datetime import datetime


class UsuariosBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    usuario: str
    nombre_1ro: str
    nombre_2do: str | None
    apellido_paterno: str
    apellido_materno: str
    almacen: int
    avatar: str = 'no-avatar'



class UsuariosCreate(UsuariosBase):
    fecha_nacimiento_str: str



class Usuarios(UsuariosBase):
    id: int
    estatus: bool = True
    fecha_nacimiento: datetime
    fecha_alta: datetime = datetime.now()
