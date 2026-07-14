from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Iterator
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

# Singleton configuration
_engine = None
_SessionFactory = None

def init_db(database_url: str = "sqlite:///bughunter.db"):
    """Initialize database engine and session factory."""
    global _engine, _SessionFactory
    if _engine is None:
        # SQLite requirement: check_same_thread=False is needed for standard web/agent use
        _engine = create_engine(database_url, connect_args={"check_same_thread": False})
        _SessionFactory = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=_engine)
    return _engine

def run_migrations(database_url: str = "sqlite:///bughunter.db"):
    """Apply Alembic migrations to the database."""
    import os
    from alembic import command
    from alembic.config import Config
    from sqlalchemy import inspect
    
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    alembic_ini_path = os.path.join(root_dir, 'alembic.ini')
    
    if not os.path.exists(alembic_ini_path):
        return
        
    alembic_cfg = Config(alembic_ini_path)
    alembic_cfg.set_main_option("sqlalchemy.url", database_url)
    
    engine = get_engine()
    inspector = inspect(engine)
    
    if inspector.has_table('job_sessions') and not inspector.has_table('alembic_version'):
        command.stamp(alembic_cfg, "head")
        
    command.upgrade(alembic_cfg, "head")

def get_engine():
    """Retrieve the SQLAlchemy engine."""
    if _engine is None:
        init_db()
    return _engine

def get_session_factory():
    """Retrieve the session factory."""
    if _SessionFactory is None:
        init_db()
    return _SessionFactory

@contextmanager
def get_db_session() -> Iterator[Session]:
    """Provide a transactional scope around a series of operations."""
    factory = get_session_factory()
    session = factory()
    try:
        yield session
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        raise
    finally:
        session.close()

def override_db(database_url: str):
    """Override database for testing purposes."""
    global _engine, _SessionFactory
    _engine = create_engine(database_url, connect_args={"check_same_thread": False})
    _SessionFactory = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=_engine)
    from storage.models import Base
    Base.metadata.create_all(_engine)
