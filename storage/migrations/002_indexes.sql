-- Index Creation

CREATE INDEX IF NOT EXISTS idx_scan_sessions_session_id ON scan_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_scan_sessions_target_domain ON scan_sessions(target_domain);

CREATE INDEX IF NOT EXISTS idx_targets_domain ON targets(domain);

CREATE INDEX IF NOT EXISTS idx_subdomains_session_id ON subdomains(session_id);
CREATE INDEX IF NOT EXISTS idx_subdomains_subdomain ON subdomains(subdomain);

CREATE INDEX IF NOT EXISTS idx_alive_hosts_session_id ON alive_hosts(session_id);
CREATE INDEX IF NOT EXISTS idx_alive_hosts_url ON alive_hosts(url);

CREATE INDEX IF NOT EXISTS idx_urls_session_id ON urls(session_id);
CREATE INDEX IF NOT EXISTS idx_urls_url ON urls(url);

CREATE INDEX IF NOT EXISTS idx_parameters_session_id ON parameters(session_id);
CREATE INDEX IF NOT EXISTS idx_parameters_parameter ON parameters(parameter);

CREATE INDEX IF NOT EXISTS idx_js_files_session_id ON js_files(session_id);
CREATE INDEX IF NOT EXISTS idx_js_files_url ON js_files(url);

CREATE INDEX IF NOT EXISTS idx_secrets_session_id ON secrets(session_id);
CREATE INDEX IF NOT EXISTS idx_secrets_type ON secrets(type);

CREATE INDEX IF NOT EXISTS idx_api_endpoints_session_id ON api_endpoints(session_id);
CREATE INDEX IF NOT EXISTS idx_api_endpoints_url ON api_endpoints(url);

CREATE INDEX IF NOT EXISTS idx_findings_session_id ON findings(session_id);
CREATE INDEX IF NOT EXISTS idx_findings_severity ON findings(severity);
CREATE INDEX IF NOT EXISTS idx_findings_status ON findings(status);

CREATE INDEX IF NOT EXISTS idx_task_history_session_id ON task_history(session_id);
CREATE INDEX IF NOT EXISTS idx_task_history_task_name ON task_history(task_name);

CREATE INDEX IF NOT EXISTS idx_logs_session_id ON logs(session_id);
CREATE INDEX IF NOT EXISTS idx_logs_component ON logs(component);
