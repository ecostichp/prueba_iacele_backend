from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker, declarative_base

from .config import dbConfig



# DATABASE_URL = "sqlite:///app/database.db"
# engine = create_engine( DATABASE_URL, connect_args={"check_same_thread": False} )

engine = create_engine( URL.create(**dbConfig) )



Base = declarative_base()



SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()