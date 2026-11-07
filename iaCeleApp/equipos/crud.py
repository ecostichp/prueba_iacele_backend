from sqlmodel  import Session, select, or_

from . import schema


def read_all_limit(session: Session, offset: int, limit: int|None):

    statement = select(schema.Teams).offset(offset).limit(limit)
    all = session.exec(statement).all()

    return all


def read_by_employees(id_a: int, id_b: int, session: Session):

    statement = select(schema.Teams).where(
        or_(
            schema.Teams.empleado_id_a == id_a,
            schema.Teams.empleado_id_b == id_b
        )
    )

    return session.exec(statement).first()


def read_by_id(id: int, session: Session):

    return session.get(schema.Teams, id)


def read_by_member(employee_id: int, session: Session):

    statement = select(schema.Teams).where(
        or_(
            schema.Teams.empleado_id_a == employee_id,
            schema.Teams.empleado_id_b == employee_id,
        )
    )

    return session.exec(statement).first()


def create(new_obj: schema.TeamsCreate, session: Session):
    
    db_obj = schema.Teams.model_validate(new_obj)

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    return db_obj


def update(existing_obj:schema.Teams, obj_new_vals: schema.TeamsUpdate, session: Session):
    
    obj_new_data = obj_new_vals.model_dump()
    db_obj = existing_obj.sqlmodel_update(obj_new_data)

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    return db_obj


def delete(existing_obj:schema.Teams, session: Session):
    
    session.delete(existing_obj)
    session.commit()

    return 'Equipo borrado con éxito'
