from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base




DATABASE_DEV = {
        'host' : "34.102.109.234",
        'database': "iaCeleDB",
        'user':"iaCele",
        'password':"iaCele123456"
        }

DATABASE_URL = f"postgresql+psycopg2://{DATABASE_DEV['user']}:{DATABASE_DEV['password']}@{DATABASE_DEV['host']}/{DATABASE_DEV['database']}"
engine = create_engine( DATABASE_URL )


# DATABASE_URL = "sqlite:///app/database.db"
# engine = create_engine( DATABASE_URL, connect_args={"check_same_thread": False} )



Base = declarative_base()



SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()