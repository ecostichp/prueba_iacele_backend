from sqlmodel  import Session, select
from datetime import datetime

from . import schema


async def read_all_limit(session: Session, offset: int, limit: int|None):

    statement = select(schema.Products).offset(offset).limit(limit)

    return session.exec(statement).all()


async def read_by_key(key: int, session: Session):

    statement = select(schema.Products).where(schema.Products.id_odoo == key)

    return session.exec(statement).first()


async def read_by_id(id: int, session: Session):

    return session.get(schema.Products, id)


async def create(new_obj: schema.ProductsCreate, session: Session):
    
    db_obj = schema.Products.model_validate(new_obj)

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    return db_obj


async def update(existing_obj:schema.Products, obj_new_vals: schema.ProductsUpdate, session: Session):
    
    obj_new_data = obj_new_vals.model_dump()
    db_obj = existing_obj.sqlmodel_update(obj_new_data)

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    return db_obj


async def delete(existing_obj:schema.Products, session: Session):
    
    session.delete(existing_obj)
    session.commit()

    return 'Producto borrado con éxito'
