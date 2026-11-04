from sqlmodel  import Session, select

from . import schema


async def read_all_limit(session: Session, offset: int, limit: int|None):

    statement = select(schema.Inventory_individual).offset(offset).limit(limit)
    all = session.exec(statement).all()

    return all


async def read_by_key(key: int, session: Session):

    statement = select(schema.Inventory_individual).where(schema.Inventory_individual.id_products == key)

    return session.exec(statement).first()


async def read_by_id(id: int, session: Session):

    return session.get(schema.Inventory_individual, id)


async def create(new_obj: schema.Inventory_individualCreate, session: Session):
    
    db_obj = schema.Inventory_individual.model_validate(new_obj)

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    return db_obj


async def update(existing_obj:schema.Inventory_individual, obj_new_vals: schema.Inventory_individualUpdate, session: Session):
    
    obj_new_data = obj_new_vals.model_dump()
    db_obj = existing_obj.sqlmodel_update(obj_new_data)

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    return db_obj


async def delete(existing_obj:schema.Inventory_individual, session: Session):
    
    session.delete(existing_obj)
    session.commit()

    return 'Producto borrado con éxito'
