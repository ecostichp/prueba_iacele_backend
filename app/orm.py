from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, declarative_base
from google.cloud.sql.connector import Connector

from .config import settings



# DATABASE_URL = "sqlite:///app/database.db"
# engine = create_engine( DATABASE_URL, connect_args={"check_same_thread": False} )




# helper function to return SQLAlchemy connection pool
def init_connection_pool(connector: Connector) -> Engine:
    # Python Connector database connection function
    def getconn():
        conn = connector.connect(
            settings.gcloud_sql_name, # Cloud SQL Instance Connection Name
            "pg8000",
            user= settings.gcloud_sql_user,
            password= settings.gcloud_sql_password,
            db= settings.gcloud_sql_db,
        )
        return conn

    SQLALCHEMY_DATABASE_URL = "postgresql+pg8000://"

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL , creator=getconn
    )
    return engine

# initialize Cloud SQL Python Connector
connector = Connector()

# create connection pool engine
engine = init_connection_pool(connector)



Base = declarative_base()



SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()