import psycopg2

from orm import DATABASE_DEV



def connect_to_dev_db():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**DATABASE_DEV)
		
        # create a cursor
        cur = conn.cursor()
        
	# execute a statement
        print('¡Connection succes! PostgreSQL database version:')
        cur.execute(f"SELECT row_to_json(t) FROM (SELECT * FROM pg_stat_activity WHERE datname='{DATABASE_DEV['database']}') t")

        # display the PostgreSQL database server version
        all_activity = cur.fetchall()
        print('\n\nHay', len(all_activity), 'actividades')
        for activity in all_activity:
            print('\n\n<> ',activity)
       
	# close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as err:
        print(err)
    
    finally:
        if conn is not None:
            conn.close()
            print('\n\nSon todas las sesiones de actividad.\n')


if __name__ == '__main__':
    connect_to_dev_db()