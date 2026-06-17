from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

class CheckpointManager:
    def __init__(self, db_path: str = ":memory:"):
        # Hidden SqliteSaver internally
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._saver = SqliteSaver(self.conn)

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
