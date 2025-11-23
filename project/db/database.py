from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from project.core.main.config import settings

from .models import Base



engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def create_db_and_tables():
    Base.metadata.create_all(engine)

def get_session():
    db = session()
    try:
        yield db
    finally:
        db.close()



