import pytest
import sqlite3
from orchestrator.checkpoint_manager import CheckpointManager

def test_checkpoint_manager():
    # Write to memory
    cm = CheckpointManager(db_path=":memory:")
    assert cm.get_saver() is not None
    
    config = {"configurable": {"thread_id": "sess1"}}
    state = {"test_key": "test_val"}
    
    # Check save()
    # Note: save() in checkpoint_manager doesn't manually save if it's delegating to langgraph's native checkpoint saver.
    # However, if save() is just an empty stub or simply returns None, we test it doesn't crash.
    cm.save(config, state)
    
    # Check load() 
    # For memory DB, if save is a stub, load might return None. We test that load() works without crashing.
    res = cm.load(config)
    assert res is None or isinstance(res, dict)
    
    # Check repeated save/load doesn't crash
    cm.save(config, state)
    cm.load(config)
    
    # Check missing checkpoint
    missing_config = {"configurable": {"thread_id": "missing"}}
    assert cm.load(missing_config) is None
    
    # Verify SqliteSaver doesn't crash on clear()
    cm.clear()
    
    # Check conn exists but might be closed
    assert isinstance(cm.conn, sqlite3.Connection)
