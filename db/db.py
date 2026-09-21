from typing import Annotated, Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import  sessionmaker, Session
from fastapi import Depends

DATABASE_URL =  "postgresql://neondb_owner:npg_Ty9FCg7fnixG@ep-noisy-breeze-b3nh4nzf-pooler.c-4.ap-southeast-1.aws.neon.tech/civicHelp?sslmode=require&channel_binding=require"


is_sqlite = DATABASE_URL.startswith("sqlite")


connect_args = {"check_same_thread": False} if is_sqlite else {}


engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=True, 
)


SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)




def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# db dependency 
db_dependency = Annotated[Session, Depends(get_db)]