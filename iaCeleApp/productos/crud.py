from sqlalchemy.orm import Session
from datetime import datetime
import json

from . import model, schema


async def get_all_products(db: Session):
    productos = db.query(model.Productos).all()

    return list(map(schema.Productos.model_validate, productos))


async def get_product_by_id(db: Session, product_id: int):
    
    return db.query(model.Productos).filter(model.Productos.id == product_id).first()


async def get_product_by_codigo(db: Session, product_codigo: int):

    return db.query(model.Productos).filter(model.Productos.codigo == product_codigo).first()



async def create_product(db: Session, producto: schema.ProductosCreate):

    fecha_ultima_compra_parse = datetime.strptime(producto.fecha_ultima_compra_str, r"%d/%m/%Y")
    fecha_ultima_venta_parse = datetime.strptime(producto.fecha_ultima_venta_str, r"%d/%m/%Y")


    db_product = model.Productos(
        codigo = producto.codigo,
        descripcion = producto.descripcion,
        linea = producto.linea,
        existencia = producto.existencia,
        ultimo_costo = producto.ultimo_costo,
        cantidad_ventas_anuales = producto.cantidad_ventas_anuales,
        monto_ventas_anuales = producto.monto_ventas_anuales,
        fecha_ultima_compra = fecha_ultima_compra_parse,
        fecha_ultima_venta = fecha_ultima_venta_parse
    )

    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return db_product


async def delete_product(db: Session, existing_product: schema.Productos):

    db.delete(existing_product)
    db.commit()

    return 'Product deleted: ok'


async def update_product(db: Session, values:str, existing_product: schema.Productos):

    values_dict = "{" + values + "}"
    values_json = json.loads(values_dict)
    key_values = values_json.keys()

    for key in key_values:    
        match key:
            case 'descripcion':
                existing_product.descripcion = values_json[key]
            
            case 'estatus':
                existing_product.estatus = values_json[key]
            
            case 'linea':
                existing_product.linea = values_json[key]
            
            case 'existencia':
                existing_product.existencia = values_json[key]
            
            case 'ultimo_costo':
                existing_product.ultimo_costo = values_json[key]
            
            case 'cantidad_ventas_anuales':
                existing_product.cantidad_ventas_anuales = values_json[key]
            
            case 'monto_ventas_anuales':
                existing_product.monto_ventas_anuales = values_json[key]
            
            case 'fecha_ultima_compra':
                fecha_ultima_compra_parse = datetime.strptime(values_json[key], r"%d-%m-%Y")
                existing_product.fecha_ultima_compra = fecha_ultima_compra_parse

            case 'fecha_ultima_venta':
                fecha_ultima_venta_parse = datetime.strptime(values_json[key], r"%d-%m-%Y")
                existing_product.fecha_ultima_venta = fecha_ultima_venta_parse

            case _:
                pass

    db.commit()
    return 'Product update: ok'
