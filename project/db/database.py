from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .models import Base



engine = create_engine('sqlite:///Db.db')
session = sessionmaker(bind=engine)

def create_db_and_tables():
    Base.metadata.create_all(engine)

def get_session():
    with session() as session:
        yield session



