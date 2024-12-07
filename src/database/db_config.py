# Setup a sqlmodel database connection
from sqlmodel import SQLModel, Session, create_engine
from src.config.settings import settings

engine = create_engine(settings.DATABASE_URL, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()
