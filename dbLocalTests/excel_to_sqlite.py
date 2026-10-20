import pandas as pd
import numpy as np
from dbConnect import dbConfigLocal
import psycopg2
import sqlite3
from datetime import datetime

# Nombre del archivo excel donde están los datos.
archivo_excel = './dbLocalTests/datos.xlsx'


def datetime_parse_pdSerie(serie):
    lista = []
    for i in serie:
        if i is np.nan:
            lista.append(None)
            continue
        lista.append(str(datetime.strptime(i, r"%d/%m/%Y")))
    return lista


def excel_to_pandasDF_usuarios():
    '''Función que retorna el DataFrame de la hoja usuarios'''    
    
    df1 = pd.read_excel(archivo_excel, 'usuarios')
    df1['fecha_nacimiento'] = datetime_parse_pdSerie(df1['fecha_nacimiento'])
    df1['fecha_alta'] = str(datetime.now())

    # Reemplazar NaN por None para compatibilidad con SQL
    df = df1.replace({np.nan: None})
    
    # Convertir a matriz de numpy, luego a lista de Python, y finalmente a tuplas
    # Esto garantiza que NO queden objetos Series de Pandas
    bulk_data = [tuple(fila) for fila in df.to_numpy().tolist()]
    return bulk_data



dfUsuarios = excel_to_pandasDF_usuarios()
query_dfUsuarios = '''
    INSERT INTO usuarios 
        (usuario,
        estatus,
        nombre_1ro,
        nombre_2do,
        apellido_paterno,
        apellido_materno,
        almacen,
        fecha_nacimiento,
        avatar,
        fecha_alta)
    VALUES
        (?,?,?,?,?,?,?,?,?,?)
    '''


def excel_to_pandasDF_productos():
    '''Función que retorna el DataFrame de la hoja productos'''    
    
    df1 = pd.read_excel(archivo_excel, 'productos')
    df1['Fecha de última compra'] = datetime_parse_pdSerie(df1['Fecha de última compra'])
    df1['Fecha de última venta'] = datetime_parse_pdSerie(df1['Fecha de última venta'])
    # Reemplazar NaN por None para compatibilidad con SQL
    df = df1.replace({np.nan: None})
    
    # Convertir a matriz de numpy, luego a lista de Python, y finalmente a tuplas
    bulk_data = [tuple(fila) for fila in df.to_numpy().tolist()]
    return bulk_data

dfProductos = excel_to_pandasDF_productos()
query_dfProductos = '''
    INSERT INTO productos 
        (codigo,
        descripcion,
        estatus,
        linea,
        fecha_ultima_compra,
        fecha_ultima_venta,
        existencia,
        ultimo_costo,
        cantidad_ventas_anuales,
        monto_ventas_anuales)
    VALUES
        (?,?,?,?,?,?,?,?,?,?)
    '''


def insert_to_sql(query, dataframe, motor='sqlite'):
    '''
    Inserta datos en la BD. 
    Parámetro 'motor': 'sqlite' o 'postgres'
    '''
    # Limpiamos espacios/saltos de línea y extraemos el nombre de la tabla de forma segura
    query_limpio = " ".join(query.split())
    try:
        # En 'INSERT INTO nombre_tabla ...', la tabla es la tercera palabra (índice 2)
        tabla = query_limpio.split(' ')[2]
    except IndexError:
        tabla = "desconocida"

    conn = None
    db_file = './iaCeleApp/database/local_iaCele.db'
    
    # Adaptar los placeholders según el motor de base de datos elegido
    if motor == 'sqlite':
        query = query.replace('%s', '?')
    
    try:
        if motor == 'sqlite':
            print('\nIniciando conexión a la base de datos SQLite de manera local...')
            conn = sqlite3.connect(db_file)
        elif motor == 'postgres':
            print('\nIniciando conexión a la base de datos PostgreSQL en el servidor de Google Cloud...')
            conn = psycopg2.connect(**dbConfigLocal)
        else:
            raise ValueError("Motor no válido. Elige 'sqlite' o 'postgres'.")

        cur = conn.cursor()
        print('>>> ¡Conexión exitosa!')
        print(f'\nTratando de insertar los datos en la tabla "{tabla}"...')
        
        cur.executemany(query, dataframe)
        conn.commit()
        
        cur.close()
        print('Se insertaron con éxito los datos.')
        
    except Exception as error:
        print('\nHubo un error real en la base de datos...')
        import traceback
        # Esto te mostrará la línea exacta y la razón del fallo si la BD rechaza los datos
        traceback.print_exc() 
    finally:
        if conn is not None:
            conn.close()
            print('Se cerró la conexión a la base de datos.\n')



if __name__ == '__main__':
    insert_to_sql(query_dfUsuarios, dfUsuarios, 'sqlite')
    insert_to_sql(query_dfProductos, dfProductos, 'sqlite')