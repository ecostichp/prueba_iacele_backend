import asyncio
import asyncpg
from dateutil import tz

from config import dbConfigLocal



async def open_sessions_PostgreSQL():
    """ Get open sessions to a particular DB in PostgreSQL """

    conn = None
    try:
        # connect to the PostgreSQL server
        print('\n Iniciando conexión a la base de datos PostgreSQL en el servidor de Google Cloud...')
        conn = await asyncpg.connect(**dbConfigLocal)
		
	    # execute a statement
        all_activity = await conn.fetch(f"SELECT * FROM pg_stat_activity WHERE datname='{dbConfigLocal['database']}'")
        print(f"\n>>> ¡Conexión exitosa! Las sesiones en la base de datos {dbConfigLocal['database']} son:")
        print('\n\nHay', len(all_activity), 'actividades:')
        i = 1
        for activity in all_activity:
            act = dict(activity)
            print(f'\n<Actividad {i}>')
            print('   ','Usuario:',act['usename'])
            print('   ','Dirección IP:',act['client_addr'])
            print('   ','Query:',act['query'])
            print('   ','Fecha Local del Query:',act['query_start'].astimezone(tz.tzlocal()))
            i += 1
       
    except Exception as err:
        # Catch the error
        print('\n>>> ¡Hubo un error con la conexión!:')
        print(err)
        print('\n')
    
    finally:
        # close the communication with the PostgreSQL
        if conn is not None:
            await conn.close()
            print('\n\nSon todas las sesiones de actividad. Se cerró la conexión a la base de datos.\n')


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(open_sessions_PostgreSQL())