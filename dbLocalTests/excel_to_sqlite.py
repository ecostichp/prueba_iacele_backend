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
    df = df1.replace(np.nan, None)
    
    bulk_data=[]
    for index, col in df.iterrows():
        data = (col)
        bulk_data.append(data)

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
    df = df1.replace(np.nan, None)

    bulk_data=[]
    for index, col in df.iterrows():
        data = (col)
        bulk_data.append(data)

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


def insert_to_sql(query, dataframe):
    
    tabla = query.split(' ', maxsplit=7)[6]

    conn = None

    
    # # Para la conexión local en SQLite
    # db_file = './iaCeleApp/database/local_iaCele.db'
    # try:
    #     # connect to the SQLite Local
    #     print('\n Iniciando conexión a la base de datos SQLite de manera local...')
    #     conn = sqlite3.connect(db_file)

    # Para la conexión con PostgreSQL en Google
    try:
        # connect to the PostgreSQL server
        print('\n Iniciando conexión a la base de datos PostgreSQL en el servidor de Google Cloud...')
        conn = psycopg2.connect(**dbConfigLocal)


        # create a cursor
        cur = conn.cursor()
        
	    # execute a statement
        print('>>> ¡Conexión exitosa!')
        print(f'\nTratando de insertar los datos en la tabla {tabla}...')
        
        cur.executemany(query, dataframe)
        conn.commit()

	    # close the communication with the PostgreSQL
        cur.close()
        print('Se insertaron con éxito los datos.')

    except Exception as error:
        print('\nHubo un error...')
        print(error)
    
    finally:
        if conn is not None:
            conn.close()
            print('Se cerró la conexión a la base de datos.\n')



if __name__ == '__main__':
    insert_to_sql(query_dfUsuarios, dfUsuarios)
    insert_to_sql(query_dfProductos, dfProductos)