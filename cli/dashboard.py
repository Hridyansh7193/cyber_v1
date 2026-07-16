from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from cli.dependencies import persistence_service

def render_final_dashboard(job_id: str):
    console = Console()
    session = persistence_service.get_session(job_id)
    if not session:
        return

    findings = persistence_service.get_findings_for_session(job_id)
    logs = persistence_service.get_logs_for_session(job_id)

    # Get canonical error count from the generated report
    error_count = 0
    status = "PASS"
    try:
        from cli.dependencies import workspace_service
        from services.target_service import TargetService
        import json
        
        normalized_target = TargetService.normalize_target(session.target_domain, job_id).domain
        session_dir = workspace_service.workspace_manager.get_session_dir(normalized_target, job_id)
        report_json_path = session_dir / "reports" / "report.json"
        
        if report_json_path.exists():
            with open(report_json_path, "r", encoding="utf-8") as f:
                report_data = json.load(f)
                error_count = report_data.get("error_count", 0)
                status = report_data.get("status", "PASS")
    except Exception:
        pass

    # Calculate Quality Score
    score = 100
    warnings = 0
    score -= (error_count * 5)
    score -= (warnings * 2)
    score += len(findings)
    score = max(0, min(100, score)) # Cap between 0 and 100
    
    score_color = "green" if score >= 80 else "yellow" if score >= 50 else "red"

    console.print("\n")
    console.print(Panel(f"[bold]Scan Completed:[/bold] {session.target_domain}\n[bold]Job ID:[/bold] {job_id}\n[bold]Status:[/bold] {status}", border_style="blue"))
    
    # Execution Summary
    summary_table = Table(show_header=False, box=None)
    summary_table.add_row("[bold]Quality Score:[/bold]", f"[{score_color}]{score}/100[/{score_color}]")
    summary_table.add_row("[bold]Findings:[/bold]", str(len(findings)))
    summary_table.add_row("[bold]Errors:[/bold]", str(error_count))
    summary_table.add_row("[bold]Warnings:[/bold]", str(warnings))
    
    console.print(summary_table)
    console.print("\n")

    # Plugins Summary (if we had execution telemetry persisted, we would query it here)
    # For now, we list findings by category
    if findings:
        findings_table = Table(title="Findings Summary")
        findings_table.add_column("Severity", style="cyan")
        findings_table.add_column("Count", style="magenta")
        
        counts = {}
        for f in findings:
            severity = getattr(f, "severity", "unknown")
            counts[severity] = counts.get(severity, 0) + 1
            
        for t, c in counts.items():
            findings_table.add_row(t, str(c))
            
        console.print(findings_table)
    
    console.print(f"\n[dim]Run `bughunter report {job_id}` for more details.[/dim]")
