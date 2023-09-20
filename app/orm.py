from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker, declarative_base

from .config import dbConfig


# # Para correr la aplicación de manera local (modo Dev),
# # con la base de datos local SQLite (modo test).
# DATABASE_URL = "sqlite:///app/database.db"
# engine = create_engine( DATABASE_URL, connect_args={"check_same_thread": False} )


# # Para correr la aplicación de manera local (modo Dev),
# # con la base de datos de producción PostgreSQL en Gcloud.
# from urllib.parse import quote_plus
# password = quote_plus(dbConfig['password'])
# dbURL = f"postgresql+psycopg2://{dbConfig['username']}:{password}@34.102.109.234/{dbConfig['database']}"
# engine = create_engine(dbURL)


# Para correr la aplicación en en GCloud Run (modo Production) contenerizada en Docker,
# con la base de datos de producción PostgreSQL en Gcloud,
# por medio de de la conexción local Unix_Socket.
engine = create_engine(URL.create(**dbConfig))


Base = declarative_base()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
