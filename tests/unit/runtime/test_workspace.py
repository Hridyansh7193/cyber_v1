import pytest
from pathlib import Path
from runtime.workspace import WorkspaceManager

def test_workspace_initialization():
    ws = WorkspaceManager("test_workspace")
    ws.initialize()
    assert ws.verify_integrity() is True
    assert ws.root_dir.exists()
    
    # Clean up
    import shutil
    shutil.rmtree("test_workspace")

def test_create_and_list_sessions():
    ws = WorkspaceManager("test_workspace")
    ws.initialize()
    try:
        session_dir = ws.create_session("session_1", "test.com", "recon")
        assert session_dir.exists()
        assert (session_dir / "reports").exists()
        
        sessions = ws.list_sessions("test.com")
        assert len(sessions) == 1
        assert sessions[0].session_id == "session_1"
        assert sessions[0].target == "test.com"
        assert sessions[0].profile == "recon"
    finally:
        import shutil
        shutil.rmtree("test_workspace")

def test_archive_session():
    ws = WorkspaceManager("test_workspace")
    ws.initialize()
    try:
        session_dir = ws.create_session("session_1", "test.com", "recon")
        archive_path = ws.archive_session("test.com", "session_1")
        
        assert Path(archive_path).exists()
        assert archive_path.endswith(".zip")
    finally:
        import shutil
        shutil.rmtree("test_workspace")
