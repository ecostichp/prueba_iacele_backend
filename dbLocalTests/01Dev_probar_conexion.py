import psycopg2

from dbConnect import dbConfig



def connect_to_PostgreSQL():
    """ Connect to the PostgreSQL database server """

    conn = None
    try:
        # connect to the PostgreSQL server
        print('\n Iniciando conexión a la base de datos PostgreSQL en el servidor de Google Cloud...')
        conn = psycopg2.connect(**dbConfig)

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        cur.execute('SELECT version()')

        # fetch the results
        db_version = cur.fetchall()
        print('\n>>> ¡Conexión exitosa! La versión de PostgreSQL es:')
        print('   ',db_version[0][0])

        # close the cursor
        cur.close()
    
    except Exception as err:
        # Catch the error
        print('\n>>> ¡Hubo un error con la conexión!:')
        print(err)
        print('\n')

    finally:
        # close the communication with the PostgreSQL
        if conn is not None:
            conn.close()
            print('\nSe cerró la conexión a la base de datos.\n')



if __name__ == '__main__':
    connect_to_PostgreSQL()