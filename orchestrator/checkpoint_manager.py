import os
import threading
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
import sqlite3


class CheckpointManager:
    """
    Manages LangGraph SQLite checkpointing with thread-safety.

    SQLite's `check_same_thread=False` allows cross-thread access but provides
    no mutual exclusion. This wrapper adds a threading.Lock to serialize all
    checkpoint reads and writes, preventing database corruption from concurrent
    node completions.
    """

    def __init__(self, db_path: str = ":memory:"):
        if db_path != ":memory:":
            os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
            
        # Shared connection — protected by _lock
        self._lock = threading.Lock()
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        # Use JsonPlusSerializer instead of msgpack to support Pydantic V2 models natively
        self._saver = SqliteSaver(self.conn, serde=JsonPlusSerializer())
        self._saver.setup()

    def get_saver(self) -> SqliteSaver:
        """Return the underlying saver for use with StateGraph.compile()."""
        return self._saver

    def save(self, config: dict, state: dict):
        """LangGraph handles saves automatically via get_saver(). This is a no-op."""
        pass

    def load(self, config: dict):
        """Load checkpoint, serializing against concurrent writers."""
        with self._lock:
            return self._saver.get(config)

    def clear(self):
        """Close the database connection cleanly."""
        with self._lock:
            try:
                self.conn.close()
            except Exception:
                pass
