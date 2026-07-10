import pytest
from unittest.mock import patch
from sqlalchemy import event
from storage.repositories import FindingRepository, SessionRepository
from schemas.finding import Finding, Severity, Confidence

@pytest.fixture
def statement_counter(db_session):
    class Counter:
        inserts = 0
        selects = 0
        commits = 0
        rollbacks = 0

    counter = Counter()

    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        if statement.lower().startswith("insert"):
            counter.inserts += 1
        elif statement.lower().startswith("select"):
            counter.selects += 1

    def after_commit(session):
        counter.commits += 1

    def after_rollback(session):
        counter.rollbacks += 1

    event.listen(db_session.bind, "before_cursor_execute", before_cursor_execute)
    event.listen(db_session, "after_commit", after_commit)
    event.listen(db_session, "after_rollback", after_rollback)

    yield counter

    event.remove(db_session.bind, "before_cursor_execute", before_cursor_execute)
    event.remove(db_session, "after_commit", after_commit)
    event.remove(db_session, "after_rollback", after_rollback)

def test_commit_count_successful_batch(db_session, statement_counter):
    SessionRepository().create(db_session, "sess_commit", "example.com")
    # Reset counts because SessionRepository.create commits
    statement_counter.commits = 0
    statement_counter.inserts = 0
    
    repo = FindingRepository()
    findings = [
        Finding(title=f"F{i}", severity=Severity.HIGH, confidence=Confidence.CERTAIN, evidence="E")
        for i in range(10)
    ]
    
    with patch.object(db_session, 'commit', wraps=db_session.commit) as mock_commit:
        repo.create_bulk(db_session, "sess_commit", findings)
        assert mock_commit.call_count == 1
        assert statement_counter.commits == 1

def test_commit_count_empty_batch(db_session, statement_counter):
    repo = FindingRepository()
    statement_counter.commits = 0
    
    with patch.object(db_session, 'commit', wraps=db_session.commit) as mock_commit:
        repo.create_bulk(db_session, "sess_commit", [])
        assert mock_commit.call_count == 0
        assert statement_counter.commits == 0
        assert statement_counter.inserts == 0

def test_rollback_db_integrity(db_session, statement_counter):
    SessionRepository().create(db_session, "sess_rollback", "example.com")
    from storage.repositories import URLRepository
    repo = URLRepository()
    
    # Pre-insert some rows
    repo.create_bulk(db_session, [{"session_id": "sess_rollback", "url": "http://1"}])
    
    db_session.commit() # ensure clean state
    rows_before = len(repo.get_by_session(db_session, "sess_rollback"))
    assert rows_before == 1
    
    statement_counter.rollbacks = 0
    statement_counter.commits = 0
    
    # Force failure using an invalid dictionary missing NOT NULL field "url"
    entities = [
        {"session_id": "sess_rollback", "url": "http://2"},
        {"session_id": "sess_rollback"} # missing url
    ]
    
    with patch.object(db_session, 'rollback', wraps=db_session.rollback) as mock_rollback:
        with pytest.raises(Exception):
            repo.create_bulk(db_session, entities)
            
        assert mock_rollback.call_count == 1
        assert statement_counter.rollbacks == 1
        assert statement_counter.commits == 0
        
    # Verify rows_after == rows_before
    from storage.models import UrlModel
    rows_after = len(db_session.query(UrlModel).filter_by(url="http://2").all())
    assert rows_after == 0
    assert len(repo.get_by_session(db_session, "sess_rollback")) == rows_before

def test_ordering_validation(db_session):
    SessionRepository().create(db_session, "sess_order", "example.com")
    repo = FindingRepository()
    
    total_items = 1000
    findings = [
        Finding(title=f"Order_{i}", severity=Severity.HIGH, confidence=Confidence.CERTAIN, evidence="E")
        for i in range(total_items)
    ]
    
    repo.create_bulk(db_session, "sess_order", findings)
    
    db_results = repo.get_by_session(db_session, "sess_order")
    
    assert len(db_results) == total_items
    for i, result in enumerate(db_results):
        assert result.title == f"Order_{i}"
