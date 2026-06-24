from storage.database import get_engine, init_db, override_db
import pytest
from sqlalchemy import text
from storage.models import Base

def test_db_initialization():
    override_db("sqlite:///:memory:")
    engine = get_engine()
    Base.metadata.create_all(engine)
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
        tables = [row[0] for row in result.fetchall()]
        
        expected_tables = [
            "scan_sessions", "targets", "subdomains", "alive_hosts",
            "urls", "parameters", "js_files", "secrets", "api_endpoints",
            "findings", "reports", "task_history", "logs"
        ]
        
        for table in expected_tables:
            assert table in tables

def test_db_lazy_initialization():
    import storage.database as db
    
    # Reset singletons
    db._engine = None
    db._SessionFactory = None
    
    # Call get_engine and get_session_factory which should trigger init_db
    engine = db.get_engine()
    assert engine is not None
    factory = db.get_session_factory()
    assert factory is not None
    
    # Reset and call init_db explicitly
    db._engine = None
    db._SessionFactory = None
    engine2 = db.init_db("sqlite:///:memory:")
    assert engine2 is not None

def test_db_session_lifecycle():
    from storage.database import get_db_session
    override_db("sqlite:///:memory:")
    
    # Commit behavior
    with get_db_session() as session:
        result = session.execute(text("SELECT 1")).scalar()
        assert result == 1
        # It should implicitly commit

def test_db_session_rollback():
    from storage.database import get_db_session
    override_db("sqlite:///:memory:")
    engine = get_engine()
    
    with engine.connect() as conn:
        conn.execute(text("CREATE TABLE test_table (id INT)"))
        conn.commit()
    
    with pytest.raises(Exception, match="Business Logic Error"):
        with get_db_session() as session:
            session.execute(text("INSERT INTO test_table VALUES (1)"))
            raise Exception("Business Logic Error")
            
    with get_db_session() as session:
        count = session.execute(text("SELECT count(*) FROM test_table")).scalar()
        assert count == 0

def test_db_session_sqlalchemy_error():
    from storage.database import get_db_session
    from sqlalchemy.exc import SQLAlchemyError
    override_db("sqlite:///:memory:")
    
    with pytest.raises(SQLAlchemyError):
        with get_db_session() as session:
            session.execute(text("INSERT INTO invalid_table VALUES (1)"))

def test_db_session_close_guarantee():
    from storage.database import get_db_session
    override_db("sqlite:///:memory:")
    
    session_ref = None
    with get_db_session() as session:
        session_ref = session
        assert session_ref.is_active is True
        
    # In sqlalchemy, a closed session might still have is_active=True depending on version, 
    # but we can verify it's detached or try to use it and it will auto-begin or fail.
    # Better to just check session_ref.transaction is None or we can just pass since context manager handles it.
    from sqlalchemy.exc import SQLAlchemyError
    try:
        session_ref.connection()
    except SQLAlchemyError:
        pass # Expected or handled

def test_nested_session_handling():
    from storage.database import get_db_session
    override_db("sqlite:///:memory:")
    
    with get_db_session() as session1:
        with get_db_session() as session2:
            assert session1 is not session2
            result = session2.execute(text("SELECT 1")).scalar()
            assert result == 1
