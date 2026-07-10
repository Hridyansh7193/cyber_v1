# Data Ownership Policy

To prevent "everyone modifies everything" bugs and race conditions, BugHunter enforces strict data ownership across all major state objects.

## Core Objects

### 1. ExecutionState
- **Owner**: `plugin_executor`
- **Modified by**: `wrapper_result_applier` (exclusively, after successful tool execution)
- **Read by**: `report_generator`, `persistence_service`, and all plugins during execution.

### 2. Report
- **Owner**: `report_generator`
- **Modified by**: None (Immutable once generated)
- **Read by**: End user, `export` CLI commands.

### 3. Telemetry
- **Owner**: `telemetry_service` (or `persistence_service`)
- **Modified by**: Only via append-only logs from components.
- **Read by**: Final dashboard, `inspect` CLI command.

### 4. Workspace
- **Owner**: `workspace_manager`
- **Modified by**: Orchestrator (creating session dirs), plugins (writing evidence via safe path functions).
- **Read by**: Plugins, `report_generator`.

### 5. Database (SQLite)
- **Owner**: `persistence_service`
- **Modified by**: Core orchestrator lifecycle hooks.
- **Read by**: Any CLI command requiring historical data.

### 6. Evidence
- **Owner**: Plugins (during execution) -> Handed off to `workspace_manager`
- **Modified by**: Append-only by executing plugins.
- **Read by**: User (for triage), False-Negative Analyzer.
