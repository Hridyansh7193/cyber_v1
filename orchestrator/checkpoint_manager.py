import os
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

class CheckpointManager:
    def __init__(self, db_path: str = ":memory:"):
        if db_path != ":memory:":
            os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
            
        # Hidden SqliteSaver internally
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._saver = SqliteSaver(self.conn)
        self._saver.setup()

    def get_saver(self):
        return self._saver

    def save(self, config: dict, state: dict):
        # We allow langgraph to handle saves via get_saver passing it to StateGraph
        pass
        
    def load(self, config: dict):
        return self._saver.get(config)
        
    def clear(self):
        # Cleanup
        self.conn.close()

