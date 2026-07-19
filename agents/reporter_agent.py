import uuid
from schemas.state import ExecutionState
from config.schemas import BugHunterConfig
from schemas.report import Report, ReportFormat
from agents.deltas import ReportDelta

def generate_reports(state: ExecutionState, config: BugHunterConfig) -> ReportDelta:
    from schemas.report import PluginSummary, TimelineEntry
    from datetime import datetime, timezone

    reports = []
    target_id = state.target.session_id
    report_time = state.target.start_time
    
    from datetime import timedelta
    
    # Calculate end time and duration deterministically based on logs
    # Since tools can run in parallel, sum of execution_time is an approximation of total CPU time,
    # but we'll use it to ensure the report generation is a pure function.
    if state.logs:
        duration_secs = int(sum(log.execution_time for log in state.logs))
    else:
        duration_secs = 0
        
    end_time_dt = report_time + timedelta(seconds=duration_secs)
    duration_str = f"{duration_secs}s"

    # Process telemetry
    timeline = []
    plugin_summaries = []
    failed_plugins = []
    error_count = 0
    
    measured_metrics = []
    has_httpx = False
    has_katana = False
    has_api = False
    has_js = False
    has_subfinder = False

    for log in state.logs:
        timeline.append(TimelineEntry(plugin=log.tool, runtime=f"{log.execution_time:.2f}s"))
        
        ps_status = "PASS"
        reason = ""
        if not log.success or log.exit_code != 0:
            ps_status = "FAIL"
            reason = "Non-zero exit code or execution failed"
            error_count += 1
            if log.tool not in failed_plugins:
                failed_plugins.append(log.tool)
        
        plugin_summaries.append(PluginSummary(
            plugin=log.tool,
            version=log.version or "unknown",
            runtime=f"{log.execution_time:.2f}s",
            results=log.parsed_objects if log.parsed_objects else 0,
            status=ps_status,
            reason=reason
        ))

        # Check success for measured metrics
        if ps_status == "PASS":
            if log.tool == "httpx": has_httpx = True
            elif log.tool in ["katana", "gau", "hakrawler", "waybackurls"]: has_katana = True
            elif log.tool in ["linkfinder", "secretfinder"]: has_js = True
            elif log.tool in ["swagger", "graphql_discovery"]: has_api = True
            elif log.tool in ["subfinder", "assetfinder"]: has_subfinder = True

    if has_httpx: measured_metrics.append("alive_hosts")
    if has_katana: measured_metrics.append("urls")
    if has_js: 
        measured_metrics.append("javascript")
        measured_metrics.append("secrets")
    if has_api:
        measured_metrics.append("apis")
    if has_subfinder: measured_metrics.append("subdomains")

    if error_count == 0:
        scan_status = "PASS"
    elif error_count < len(state.logs) and len(state.logs) > 0:
        scan_status = "PARTIAL"
    else:
        scan_status = "FAIL"

    for fmt_str in config.reporting.report_formats:
        try:
            fmt = ReportFormat(fmt_str)
            deterministic_id = uuid.uuid5(uuid.NAMESPACE_URL, f"{target_id}:{fmt_str}")
            
            from schemas.report import DiscoveredAssets
            fuzz_res = list(state.recon_state.parameters)
            fuzz_res.extend(str(f.get("url", f)) if isinstance(f, dict) else str(f) for f in state.vuln_state.fuzz_results)
            
            js_from_urls = [u for u in state.recon_state.urls if ".js" in u.split("?")[0].lower()]
            all_js = tuple(set(list(state.js_state.js_files) + js_from_urls))
            
            assets = DiscoveredAssets(
                subdomains=state.recon_state.subdomains,
                hosts=state.recon_state.alive_hosts,
                urls=state.recon_state.urls,
                javascript=all_js,
                apis=tuple(list(state.api_state.swagger_urls) + list(state.api_state.graphql_urls)),
                secrets=tuple(s.get("secret", str(s)) if isinstance(s, dict) else str(s) for s in state.js_state.secrets),
                technologies=tuple(set(tech for techs in state.recon_state.tech_stack.values() for tech in techs)),
                takeovers=tuple(t.get("domain", str(t)) if isinstance(t, dict) else str(t) for t in state.vuln_state.takeovers),
                fuzz_results=tuple(fuzz_res),
                measured_metrics=tuple(measured_metrics)
            )
            
            tool_versions = {}
            tool_paths = {}
            skipped = []
            if state.runtime_context and state.runtime_context.tool_manager:
                for t_name, t_info in state.runtime_context.tool_manager.get_tools().items():
                    tool_versions[t_name] = t_info.version or "unknown"
                    tool_paths[t_name] = t_info.binary_path

            severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4, "UNKNOWN": 5}
            sorted_findings = tuple(sorted(state.findings, key=lambda f: (severity_order.get(str(f.severity).upper(), 5), f.id)))
            sorted_logs = tuple(sorted(state.logs, key=lambda l: l.tool))

            rep = Report(
                report_id=deterministic_id,
                session_id=target_id,
                report_path=f"{config.reporting.output_directories.get(fmt_str, 'reports')}/report.{fmt_str}",
                report_format=fmt,
                created_at=report_time,
                timestamp=report_time,
                findings=sorted_findings,
                total_findings=len(sorted_findings),
                assets=assets,
                telemetry=sorted_logs,
                intelligence=state.intelligence,
                operational=state.operational,
                tool_versions=tool_versions,
                tool_paths=tool_paths,
                skipped_plugins=tuple(skipped),
                failed_plugins=tuple(failed_plugins),
                plugin_summaries=tuple(plugin_summaries),
                timeline=tuple(timeline),
                duration=duration_str,
                start_time=report_time.isoformat(),
                end_time=end_time_dt.isoformat(),
                status=scan_status,
                error_count=error_count,
                target=state.target.resolved_url or state.target.domain
            )
            reports.append(rep)
        except ValueError:
            pass

    return ReportDelta(reports=tuple(reports))
