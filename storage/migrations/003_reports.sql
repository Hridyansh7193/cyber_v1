-- Reports Table Creation

CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    report_path TEXT NOT NULL,
    report_format TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY(session_id) REFERENCES scan_sessions(session_id)
);

CREATE INDEX IF NOT EXISTS idx_reports_session_id ON reports(session_id);
