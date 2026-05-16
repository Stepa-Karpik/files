from collections.abc import Generator
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
DATABASE_URL=os.getenv('FILES_DATABASE_URL','sqlite+pysqlite:///./files.db')
engine=create_engine(DATABASE_URL)
SessionLocal=sessionmaker(engine)
def get_session()->Generator[Session,None,None]:
    with SessionLocal() as session: yield session
