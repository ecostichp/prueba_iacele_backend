from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker, declarative_base

from .config import settings



DATABASE_URL = f"postgresql+psycopg2://{settings.gcloud_sql_user}:{settings.gcloud_sql_password}@{settings.gcloud_sql_host}/{settings.gcloud_sql_db}"
# engine = create_engine( DATABASE_URL )


# DATABASE_URL = "sqlite:///app/database.db"
# engine = create_engine( DATABASE_URL, connect_args={"check_same_thread": False} )



data = URL.create(
    drivername = "postgresql+psycopg2",
    username = settings.gcloud_sql_user,
    password = settings.gcloud_sql_password,
    database = settings.gcloud_sql_db,
    query={"unix_socket": f'/cloudsql/{settings.gcloud_sql_host}/.s.PGSQL.5432'},
)

engine = create_engine( data )







Base = declarative_base()



SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()