import pytest
from runtime.workspace import WorkspaceManager

def test_workspace_initialization():
    ws = WorkspaceManager("test_workspace")
    ws.initialize()
    assert ws.verify_integrity() is True
    assert ws.sessions_dir.exists()
    
    # Clean up
    import shutil
    shutil.rmtree("test_workspace")
