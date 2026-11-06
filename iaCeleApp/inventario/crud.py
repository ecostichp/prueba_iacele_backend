from sqlmodel  import Session, select, func, case, alias

from . import schema
from ..productos import schema as schema_productos
from ..equipos import schema as schema_equipos

async def read_all_limit(session: Session, offset: int, limit: int|None):

    statement = select(schema.Inventory).offset(offset).limit(limit)
    all = session.exec(statement).all()

    return all


async def read_by_key(key: int, session: Session):

    statement = select(schema.Inventory).where(schema.Inventory.id_products == key)

    return session.exec(statement).first()


async def read_by_id(id: int, session: Session):

    return session.get(schema.Inventory, id)


async def create(new_obj: schema.InventoryCreate, session: Session):
    
    db_obj = schema.Inventory.model_validate(new_obj)

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    return db_obj


async def delete(existing_obj:schema.Inventory, session: Session):
    
    session.delete(existing_obj)
    session.commit()

    return 'Producto borrado con éxito'


async def read_invidual_code_registers_all(employee_id: int, id_product: int, session: Session):

    statement = (
            select(
                schema.Inventory,
                schema_productos.Products.id,
                schema_productos.Products.code,
                schema_productos.Products.name,
            )
            .join(schema_productos.Products, schema.Inventory.id_products == schema_productos.Products.id)
            .where(schema.Inventory.assigned_user_id == employee_id)
            .where(schema.Inventory.count_type == 'individual')
            .where(schema.Inventory.id_products == id_product)
        )

    all_registers = session.exec(statement).all()

    if not all_registers:
        product = session.get(schema_productos.Products, id_product)
        return [
            {
                "product_id": {
                    "id": product.id if product else id_product,
                    "code": product.code if product else "",
                    "name": product.name if product else "",
                    "total_qty": 0,
                },
                "registers": [],
            }
        ]
    
    return [
        {
            "product_id": {
                "id": all_registers[0]._mapping["id"],
                "code": all_registers[0]._mapping["code"],
                "name": all_registers[0]._mapping["name"],
                "total_qty": sum(
                    reg._mapping["Inventory"].count_qty for reg in all_registers 
                    if reg._mapping["Inventory"].count_qty is not None
                ),
            },
            "registers": [dict(row._mapping['Inventory']) for row in all_registers]
        }
    ]


async def read_invidual_registers_limit(employee_id: int, session: Session, offset: int, limit: int|None):

    statement = (
            select(
                schema.Inventory.id_products,
                schema_productos.Products.code,
                schema_productos.Products.name,
                func.sum(schema.Inventory.count_qty).label("total_qty")
            )
            .join(schema_productos.Products, schema.Inventory.id_products == schema_productos.Products.id)
            .where(schema.Inventory.assigned_user_id == employee_id)
            .where(schema.Inventory.count_type == 'individual')
            .group_by(
                schema.Inventory.id_products,
                schema_productos.Products.code,
                schema_productos.Products.name
            )
            .offset(offset)
            .limit(limit)
        )

    all_registers = session.exec(statement).all()

    return [dict(row._mapping) for row in all_registers]


async def read_team_registers_limit(team: schema_equipos.Teams, session: Session, offset: int, limit: int|None):
        
    empleado_id_a = team.empleado_id_a
    empleado_id_b = team.empleado_id_b

    # 2. Definimos la estructura base de la consulta para el Empleado 1 (stmt1)
    stmt1 = (
        select(
            schema.Inventory.id_products,
            schema_productos.Products.code.label("code_a"),
            schema_productos.Products.name.label("name_a"),
            func.sum(schema.Inventory.count_qty).label("total_qty_a")
        )
        .join(schema_productos.Products, schema.Inventory.id_products == schema_productos.Products.id)
        .where(schema.Inventory.assigned_user_id == empleado_id_a)
        .where(schema.Inventory.count_type == 'individual')
        .group_by(
            schema.Inventory.id_products, 
            schema_productos.Products.code, 
            schema_productos.Products.name
        )
    ).subquery()

    # 3. Definimos la estructura base de la consulta para el Empleado 2 (stmt2)
    stmt2 = (
        select(
            schema.Inventory.id_products,
            schema_productos.Products.code.label("code_b"),
            schema_productos.Products.name.label("name_b"),
            func.sum(schema.Inventory.count_qty).label("total_qty_b")
        )
        .join(schema_productos.Products, schema.Inventory.id_products == schema_productos.Products.id)
        .where(schema.Inventory.assigned_user_id == empleado_id_b)
        .where(schema.Inventory.count_type == 'individual')
        .group_by(
            schema.Inventory.id_products, 
            schema_productos.Products.code, 
            schema_productos.Products.name
        )
    ).subquery()

    # 4. Realizamos el FULL OUTER JOIN combinando ambas subconsultas por 'id_products'
    statement = (
        select(
            func.coalesce(stmt1.c.id_products, stmt2.c.id_products).label("id_products"),
            func.coalesce(stmt1.c.code_a, stmt2.c.code_b).label("code"),
            func.coalesce(stmt1.c.name_a, stmt2.c.name_b).label("name"),
            stmt1.c.total_qty_a,
            stmt2.c.total_qty_b,
            case(
                (stmt1.c.name_a == stmt2.c.name_b, True),
                else_=False
            ).label("iguales")
        )
        .join(stmt2, stmt1.c.id_products == stmt2.c.id_products, full=True)
        .order_by("name")
        .offset(offset)
        .limit(limit)
    )

    all_registers = session.exec(statement).all()

    return [dict(row._mapping) for row in all_registers]
