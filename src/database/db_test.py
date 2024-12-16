from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base  # Your application's SQLAlchemy models

DATABASE_URL = "sqlite:///./test.db"  # Persistent SQLite database for testing

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_test_db():
    """
    Initialize the SQLite database with tables defined in models.
    """
    Base.metadata.drop_all(bind=engine)  # Drop existing tables
    Base.metadata.create_all(bind=engine)  # Recreate tables

def get_test_db():
    """
    Provides a SQLAlchemy session for testing.
    """
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()