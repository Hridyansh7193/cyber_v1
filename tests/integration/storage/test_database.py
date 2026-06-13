from storage.database import get_engine, init_db, override_db
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
