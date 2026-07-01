from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import get_settings

settings = get_settings()
engine = create_engine(
settings.DATABASE_URL,
pool_pre_ping=True, # test connection before using it
pool_size=10, # max 10 simultaneous DB connections
max_overflow=20, # allow 20 extra if pool is full
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
class Base(DeclarativeBase):
    pass
def get_db():
    '''
FastAPI dependency — use with Depends(get_db).
The 'yield' makes this a context manager:
- Code before yield = setup (create session)
- yield db = the resource is available
- Code after yield (finally) = cleanup (close session)
Session is ALWAYS closed, even if an exception occurs.
'''
    db = SessionLocal()
    try:
        yield db    
    finally:    
        db.close()