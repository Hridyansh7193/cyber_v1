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
            rep = Report(
                report_id=deterministic_id,
                session_id=target_id,
                report_path=f"{config.reporting.output_directories.get(fmt_str, 'reports')}/report.{fmt_str}",
                report_format=fmt,
                created_at=report_time,
                timestamp=report_time
            )
            reports.append(rep)
        except ValueError:
            pass  # Skip invalid formats

    return ReportDelta(reports=tuple(reports))
