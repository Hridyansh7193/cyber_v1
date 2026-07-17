"""
Versions module defining explicit compatibility metadata for all BugHunter schemas.
This avoids mixing runtime objects with compatibility metadata and enables the compatibility policy.
"""

# The interface contract that ExecutionPlugin implementers must follow.
PLUGIN_INTERFACE_VERSION = "1.0"

# The schema structure of ExecutionState passed to plugins.
STATE_SCHEMA_VERSION = "2.0"

# The structure of the generated final JSON/MD report outputs.
REPORT_SCHEMA_VERSION = "1.0"

# The execution telemetry and metrics tracing schema.
TRACE_SCHEMA_VERSION = "1.0"

# The schema definition for the persisted SQLite database.
DATABASE_SCHEMA_VERSION = "1.0"
