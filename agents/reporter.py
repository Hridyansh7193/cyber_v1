import uuid
from datetime import datetime, UTC
from schemas.state import ExecutionState
from config.schemas import BugHunterConfig
from schemas.report import Report, ReportFormat
from agents.deltas import ReportDelta

def generate_reports(state: ExecutionState, config: BugHunterConfig) -> ReportDelta:
    reports = []
    target_id = state.target.session_id
    # Use start_time as the canonical report timestamp so this function is pure/deterministic
    report_time = state.target.start_time

    for fmt_str in config.reporting.report_formats:
        try:
            fmt = ReportFormat(fmt_str)
            # Derive a deterministic UUID from session_id + format so two identical calls
            # produce identical ReportDelta values (pure function guarantee).
            deterministic_id = uuid.uuid5(uuid.NAMESPACE_URL, f"{target_id}:{fmt_str}")
            # Create typed report instances, no writing to disk
            from schemas.report import DiscoveredAssets
            assets = DiscoveredAssets(
                subdomains=state.recon_state.subdomains,
                hosts=state.recon_state.alive_hosts,
                urls=state.recon_state.urls,
                javascript=state.js_state.js_files,
                apis=tuple(list(state.api_state.swagger_urls) + list(state.api_state.graphql_urls))
            )
            tool_versions = {}
            tool_paths = {}
            skipped = []
            if state.runtime_context and state.runtime_context.tool_manager:
                for t_name, t_info in state.runtime_context.tool_manager.tools.items():
                    if t_info.installed:
                        tool_versions[t_name] = t_info.version or "unknown"
                        tool_paths[t_name] = t_info.binary_path
                    else:
                        skipped.append(t_name)

            rep = Report(
                report_id=deterministic_id,
                session_id=target_id,
                report_path=f"{config.reporting.output_directories.get(fmt_str, 'reports')}/report.{fmt_str}",
                report_format=fmt,
                created_at=report_time,
                timestamp=report_time,
                findings=state.findings,
                total_findings=len(state.findings),
                assets=assets,
                telemetry=state.logs,
                intelligence=state.intelligence,
                operational=state.operational,
                tool_versions=tool_versions,
                tool_paths=tool_paths,
                skipped_plugins=tuple(skipped)
            )
            reports.append(rep)
        except ValueError:
            pass  # Skip invalid formats

    return ReportDelta(reports=tuple(reports))
