import psycopg2
from dateutil import tz
import dateutil.parser

from dbConnect import dbConfig



def open_sessions_PostgreSQL():
    """ Get open sessions to a particular DB in PostgreSQL """

    conn = None
    try:
        # connect to the PostgreSQL server
        print('\n Iniciando conexión a la base de datos PostgreSQL en el servidor de Google Cloud...')
        conn = psycopg2.connect(**dbConfig)

        # create a cursor
        cur = conn.cursor()
		
	    # execute a statement
        cur.execute(f"SELECT row_to_json(t) FROM (SELECT * FROM pg_stat_activity WHERE datname='{dbConfig['database']}') t")

        # fetch the results
        all_activity = cur.fetchall()
        print(f"\n>>> ¡Conexión exitosa! Las sesiones en la base de datos {dbConfig['database']} son:")
        print('\n\nHay', len(all_activity), 'actividades:')

        i = 1
        for activity in all_activity:
            act = activity[0]
            print(f'\n<Actividad {i}>')
            print('   ','Usuario:',act['usename'])
            print('   ','Dirección IP:',act['client_addr'])
            print('   ','Query:',act['query'])
            print('   ','Fecha Local del Query:', dateutil.parser.isoparse(act['query_start']).astimezone(tz.tzlocal()))
            i += 1

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
            print('\n\nSon todas las sesiones de actividad. Se cerró la conexión a la base de datos.\n')


if __name__ == '__main__':
    open_sessions_PostgreSQL()