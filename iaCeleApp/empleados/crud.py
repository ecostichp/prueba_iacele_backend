from sqlmodel  import Session, select
from datetime import datetime
from sqlalchemy import text

from ..timeutil import as_utc
from . import schema


async def read_all_limit(session: Session, offset: int, limit: int|None):

    statement = select(schema.Employees).offset(offset).limit(limit)

    return session.exec(statement).all()


async def read_by_key(key: id, session: Session):

    statement = select(schema.Employees).where(schema.Employees.id_odoo == key)

    return session.exec(statement).first()


async def read_by_id(id: int, session: Session):

    return session.get(schema.Employees, id)


async def create(new_obj: schema.EmployeesCreate, session: Session):
    
    obj_data = new_obj.model_dump(
        exclude = {
            'hire_date_str'
        }
    )
    if obj_data.get('id') is None:
        obj_data.pop('id', None)
    obj_data['hire_date'] = as_utc(datetime.strptime(new_obj.hire_date_str, r"%Y-%m-%d"))

    db_obj = schema.Employees(**obj_data)

    session.add(db_obj)
    session.flush()
    if new_obj.id is not None and session.get_bind().dialect.name == "postgresql":
        session.execute(text(
            "SELECT setval(pg_get_serial_sequence('employees', 'id'), "
            "(SELECT MAX(id) FROM employees))"
        ))
    session.commit()
    session.refresh(db_obj)

    return db_obj


async def update(existing_obj:schema.Employees, obj_new_vals: schema.EmployeesUpdate, session: Session):
    
    obj_new_data = obj_new_vals.model_dump(exclude_unset=True)
    if 'hire_date' in obj_new_data.keys():
        obj_new_data['hire_date'] = as_utc(datetime.strptime(obj_new_vals.hire_date_str, r"%Y-%m-%d"))

    db_obj = existing_obj.sqlmodel_update(obj_new_data)

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    return db_obj


async def delete(existing_obj:schema.Employees, session: Session):
    
    session.delete(existing_obj)
    session.commit()

    return 'Empleado borrado con éxito'
