from sqlalchemy.orm import Session
from datetime import datetime
import json

from . import model, schema


async def get_all_users(db: Session):
    usuarios = db.query(model.Usuarios).all()

    return list(map(schema.Usuarios.model_validate, usuarios))


async def get_user_by_id(db: Session, user_id: int):
    
    return db.query(model.Usuarios).filter(model.Usuarios.id == user_id).first()


async def get_user_by_usuario(db: Session, user_usuario: str):

    return db.query(model.Usuarios).filter(model.Usuarios.usuario == user_usuario).first()



async def create_user(db: Session, usuario: schema.UsuariosCreate):

    fecha_nacimiento_parse = datetime.strptime(usuario.fecha_nacimiento_str, r"%d/%m/%Y")

    db_user = model.Usuarios(
        usuario = usuario.usuario,
        nombre_1ro = usuario.nombre_1ro,
        nombre_2do = usuario.nombre_2do,
        apellido_paterno = usuario.apellido_paterno,
        apellido_materno = usuario.apellido_materno,
        almacen = usuario.almacen,
        avatar = usuario.avatar,
        estatus = True,
        fecha_nacimiento = fecha_nacimiento_parse,
        fecha_alta = datetime.now()
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


async def delete_user(db: Session, existing_user: schema.Usuarios):

    db.delete(existing_user)
    db.commit()

    return 'User deleted: ok'


async def update_user(db: Session, values:str, existing_user: schema.Usuarios):

    values_dict = "{" + values + "}"
    values_json = json.loads(values_dict)
    key_values = values_json.keys()

    for key in key_values:    
        match key:
            case 'estatus':
                existing_user.estatus = values_json[key]
            
            case 'usuario':
                existing_user.usuario = values_json[key]
            
            case 'apellido_paterno':
                existing_user.apellido_paterno = values_json[key]
            
            case 'apellido_materno':
                existing_user.apellido_materno = values_json[key]
            
            case 'almacen':
                existing_user.almacen = values_json[key]
            
            case 'nombre_1ro':
                existing_user.nombre_1ro = values_json[key]
            
            case 'nombre_2do':
                existing_user.nombre_2do = values_json[key]
            
            case 'fecha_nacimiento':
                fecha_nacimiento_parse = datetime.strptime(values_json[key], r"%d-%m-%Y")
                existing_user.fecha_nacimiento = fecha_nacimiento_parse
            
            case 'avatar':
                existing_user.avatar = values_json[key]

            case _:
                pass

    db.commit()
    return 'User update: ok'
