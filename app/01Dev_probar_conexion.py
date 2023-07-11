import asyncio
import asyncpg

from config import dbConfig



async def connect_to_PostgreSQL():
    """ Connect to the PostgreSQL database server """

    conn = None
    try:
        # connect to the PostgreSQL server
        print('\n Iniciando conexión a la base de datos PostgreSQL en el servidor de Google Cloud...')
        conn = await asyncpg.connect(**dbConfig)

        # execute a statement
        db_version = await conn.fetch('SELECT version()')
        print('\n>>> ¡Conexión exitosa! La versión de PostgreSQL es:')
        print('   ',db_version[0])
    
    except Exception as err:
        # Catch the error
        print('\n>>> ¡Hubo un error con la conexión!:')
        print(err)
        print('\n')

    finally:
        # close the communication with the PostgreSQL
        if conn is not None:
            await conn.close()
            print('\nSe cerró la conexión a la base de datos.\n')



if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(connect_to_PostgreSQL())