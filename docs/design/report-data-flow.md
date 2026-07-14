# Report Data Flow

| Field | Producer | Canonical Owner | Persistence | Report Consumer | Current Status |
| --- | --- | --- | --- | --- | --- |
| target | ExecutionCoordinator | `ExecutionState.target.domain` | `checkpoint.json` | `Report.target` | FIXED |
| session_id | ExecutionCoordinator | `ExecutionState.target.session_id` | `checkpoint.json` | `Report.session_id` | FIXED |
| job_id | CLI / ScanService | `ExecutionState.metadata["job_id"]` | `checkpoint.json` | `Report.job_id` | FIXED |
| start_time | ExecutionCoordinator | `ExecutionState.target.start_time` | `checkpoint.json` | `Report.start_time` | FIXED |
| end_time | ExecutionCoordinator | `ExecutionState.target.end_time` | `checkpoint.json` | `Report.end_time` | FIXED |
| duration | ReporterAgent | Derived (`end_time - start_time`) | Derived in Report | `Report.duration` | FIXED |
| scan_status | ScanService | `ExecutionState.target.status` | `checkpoint.json` | `Report.status` | FIXED |
| quality_score | ReporterAgent | `reporter_agent.py` | `Report` | `Report` / CLI | FIXED |
| plugins_planned | PlannerAgent | `ExecutionState.task_queue` | `checkpoint.json` | `Report` | FIXED |
| plugins_executed | ReporterAgent | `ExecutionState.logs` (execution trace) | `checkpoint.json` | `Report.plugin_summaries` | FIXED |
| plugins_skipped | PlannerAgent | `ExecutionState.task_queue` (if task is skipped) | `checkpoint.json` | `Report.plugin_summaries` | FIXED |
| plugin_failures | PluginExecutor | `ExecutionState.logs` (exit_code/success) | `checkpoint.json` | `Report.plugin_summaries` | FIXED |
| plugin_runtime | PluginExecutor | `ExecutionState.logs` (`execution_time`) | `checkpoint.json` | `Report.plugin_summaries` | FIXED |
| plugin_version | ToolManager | `ExecutionState.logs` (`version`) | `checkpoint.json` | `Report.plugin_summaries` | FIXED |
| targets_received | PluginExecutor | `ExecutionState.logs` (`received_count` or via recon) | `checkpoint.json` | `Report` (Target Metrics) | FIXED |
| targets_filtered | PluginExecutor | `ExecutionState.logs` | `checkpoint.json` | `Report` | FIXED |
| targets_executed | PluginExecutor | `ExecutionState.logs` | `checkpoint.json` | `Report` | FIXED |
| parsed_objects | OutputParser | `ExecutionState.logs` (`parsed_objects`) | `checkpoint.json` | `Report` | FIXED |
| finding_count | ReporterAgent | `ExecutionState.findings` (len) | `checkpoint.json` | `Report` | FIXED |
| errors | PluginExecutor / Catchalls | `ExecutionState.logs` (wrapper/parser errors) | `checkpoint.json` | `Report.error_count` | FIXED |
| warnings | PluginExecutor | `ExecutionState.logs` | `checkpoint.json` | `Report` | FIXED |
| coverage | ReporterAgent | `ExecutionState.recon_state`, `js_state`, `api_state` | `checkpoint.json` | `Report.assets` | FIXED |
| timeline | ReporterAgent | `ExecutionState.logs` (sorted chronologically) | `checkpoint.json` | `Report.timeline` | FIXED |
| pipeline_health | ReporterAgent | `ExecutionState.logs` (metrics validation) | `checkpoint.json` | `Report.pipeline_health` | FIXED |
| findings | Tool Parsers / Applier | `ExecutionState.findings` | `checkpoint.json` | `Report.findings` | FIXED |
| recommendations | AnalyzerAgent / Applier | `utils/recommendations.py` -> `ExecutionState.findings` | `checkpoint.json` | `Report.findings` (recommendation) | FIXED |
| evidence references | Tool Parsers | `ExecutionState.findings` (evidence, poc, references) | `checkpoint.json` | `Report.findings` | FIXED |
