-- Initial Schema creation for all tables
-- Note: schema.sql contains the combined DDL. We replicate it here as Migration 001.

CREATE TABLE IF NOT EXISTS scan_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL UNIQUE,
    target_domain TEXT NOT NULL,
    started_at TIMESTAMP,
    finished_at TIMESTAMP,
    status TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS targets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain TEXT NOT NULL UNIQUE,
    scope_type TEXT,
    program_name TEXT,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS subdomains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    subdomain TEXT NOT NULL,
    source TEXT,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY(session_id) REFERENCES scan_sessions(session_id)
);

CREATE TABLE IF NOT EXISTS alive_hosts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    url TEXT NOT NULL,
    status_code INTEGER,
    title TEXT,
    tech_stack TEXT,
    response_time REAL,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY(session_id) REFERENCES scan_sessions(session_id)
);

CREATE TABLE IF NOT EXISTS urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    url TEXT NOT NULL,
    source TEXT,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY(session_id) REFERENCES scan_sessions(session_id)
);

CREATE TABLE IF NOT EXISTS parameters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    url TEXT NOT NULL,
    parameter TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY(session_id) REFERENCES scan_sessions(session_id)
);

CREATE TABLE IF NOT EXISTS js_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    url TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY(session_id) REFERENCES scan_sessions(session_id)
);

CREATE TABLE IF NOT EXISTS secrets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    type TEXT NOT NULL,
    value TEXT NOT NULL,
    source TEXT,
    confidence TEXT,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY(session_id) REFERENCES scan_sessions(session_id)
);

CREATE TABLE IF NOT EXISTS api_endpoints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    type TEXT NOT NULL,
    url TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY(session_id) REFERENCES scan_sessions(session_id)
);

CREATE TABLE IF NOT EXISTS findings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    title TEXT NOT NULL,
    severity TEXT NOT NULL,
    confidence TEXT NOT NULL,
    description TEXT,
    evidence TEXT,
    status TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY(session_id) REFERENCES scan_sessions(session_id)
);

CREATE TABLE IF NOT EXISTS task_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    task_name TEXT NOT NULL,
    status TEXT NOT NULL,
    attempts INTEGER DEFAULT 0,
    duration REAL,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY(session_id) REFERENCES scan_sessions(session_id)
);

CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    component TEXT NOT NULL,
    level TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY(session_id) REFERENCES scan_sessions(session_id)
);
