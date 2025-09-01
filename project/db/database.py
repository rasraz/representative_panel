from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///Db.db')
base = declarative_base()
session = sessionmaker(bind=engine)

def create_db_and_tables():
    base.metadata.create_all(engine)

def get_session():
    with session() as session:
        yield session



