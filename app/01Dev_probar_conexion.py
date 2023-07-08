import psycopg2

from orm import DATABASE_DEV



def connect_to_dev_db():

    conn = None
    try:

        # connect to the PostgreSQL server
        print('\nTratando de conectarse a PostgreSQL, de manera remota en Google Cloud SQL...')
        conn = psycopg2.connect(**DATABASE_DEV)
		
        # create a cursor
        cur = conn.cursor()
        
	# execute a statement
        print('>>> ¡Conexión exitosa! La versión de la base de datos de PostgreSQL es:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchall()
        print(db_version)
       
	# close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as err:
        print(err)
    
    finally:
        if conn is not None:
            conn.close()
            print('Se cerró la conexión a la base de datos.\n')


if __name__ == '__main__':
    connect_to_dev_db()