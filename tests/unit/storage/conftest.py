import pytest
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from storage.database import _engine, _SessionFactory, get_db_session
from sqlalchemy.orm import sessionmaker
from storage.models import Base
import storage.database as db_module

@pytest.fixture(scope="session")
def engine():
    # Setup temporary SQLite database in memory for testing
    test_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(test_engine)
    
    # Override the global engine and session factory
    db_module._engine = test_engine
    db_module._SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    return test_engine

@pytest.fixture
def db_session(engine) -> Session:
    # We clear the tables before each test
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with get_db_session() as session:
        yield session
