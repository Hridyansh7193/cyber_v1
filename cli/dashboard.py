from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from cli.dependencies import persistence_service, workspace_service

def render_final_dashboard(job_id: str):
    console = Console()
    session = persistence_service.get_session(job_id)
    if not session:
        return

    findings = persistence_service.get_findings_for_session(job_id)
    logs = persistence_service.get_logs_for_session(job_id)

    # Calculate Quality Score
    # 100 base points.
    # -5 for every ERROR log.
    # -2 for every WARNING log.
    # +1 for every finding.
    score = 100
    errors = sum(1 for log in logs if log.level == "ERROR")
    warnings = sum(1 for log in logs if log.level == "WARNING")
    score -= (errors * 5)
    score -= (warnings * 2)
    score += len(findings)
    score = max(0, min(100, score)) # Cap between 0 and 100
    
    score_color = "green" if score >= 80 else "yellow" if score >= 50 else "red"

    console.print("\n")
    console.print(Panel(f"[bold]Scan Completed:[/bold] {session.target_domain}\n[bold]Job ID:[/bold] {job_id}", border_style="blue"))
    
    # Execution Summary
    summary_table = Table(show_header=False, box=None)
    summary_table.add_row("[bold]Quality Score:[/bold]", f"[{score_color}]{score}/100[/{score_color}]")
    summary_table.add_row("[bold]Findings:[/bold]", str(len(findings)))
    summary_table.add_row("[bold]Errors:[/bold]", str(errors))
    summary_table.add_row("[bold]Warnings:[/bold]", str(warnings))
    
    console.print(summary_table)
    console.print("\n")

    # Plugins Summary (if we had execution telemetry persisted, we would query it here)
    # For now, we list findings by category
    if findings:
        findings_table = Table(title="Findings Summary")
        findings_table.add_column("Type", style="cyan")
        findings_table.add_column("Count", style="magenta")
        
        counts = {}
        for f in findings:
            counts[f.finding_type] = counts.get(f.finding_type, 0) + 1
            
        for t, c in counts.items():
            findings_table.add_row(t, str(c))
            
        console.print(findings_table)
    
    console.print(f"\n[dim]Run `bughunter report {job_id}` for more details.[/dim]")
