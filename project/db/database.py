from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .models import Base



engine = create_engine('sqlite:///Db.db', connect_args={"check_same_thread": False})
session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def create_db_and_tables():
    Base.metadata.create_all(engine)

def get_session():
    db = session()
    try:
        yield db
    finally:
        db.close()



