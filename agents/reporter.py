import datetime
from schemas.state import ExecutionState
from config.schemas import BugHunterConfig
from schemas.report import Report, ReportFormat
from agents.deltas import ReportDelta

def generate_reports(state: ExecutionState, config: BugHunterConfig) -> ReportDelta:
    reports = []
    target_id = state.target.session_id
    
    for fmt_str in config.reporting.report_formats:
        try:
            fmt = ReportFormat(fmt_str)
            # Create typed report instances, no writing to disk
            rep = Report(
                session_id=target_id,
                report_path=f"{config.reporting.output_directories.get(fmt_str, 'reports')}/report.{fmt_str}",
                report_format=fmt,
                timestamp=state.target.start_time
            )
            reports.append(rep)
        except ValueError:
            pass # Skip invalid formats
            
    return ReportDelta(reports=tuple(reports))
