import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from cli.dependencies import persistence_service, workspace_service

app = typer.Typer(help="Manage and inspect reports and session data.")
console = Console()

@app.command("report")
def report_cmd(job_id: str = typer.Argument(..., help="The Job ID to report on")):
    """Summarize persisted report metadata."""
    session = persistence_service.get_session(job_id)
    if not session:
        console.print(f"[red]Job {job_id} not found in database.[/red]")
        raise typer.Exit(code=1)
        
    reports = persistence_service.get_reports_for_session(job_id)
    if not reports:
        console.print(f"[yellow]No reports found for job {job_id}.[/yellow]")
        raise typer.Exit()
        
    table = Table(title=f"Reports for Job: {job_id}")
    table.add_column("Report ID", style="cyan")
    table.add_column("Format", style="magenta")
    table.add_column("Created At", style="green")
    
    for r in reports:
        table.add_row(str(r.id), r.report_format, str(r.created_at))
        
    console.print(table)


@app.command("export")
def export_cmd(job_id: str = typer.Argument(..., help="The Job ID to export")):
    """Create a downloadable ZIP of the session."""
    session = persistence_service.get_session(job_id)
    if not session:
        console.print(f"[red]Job {job_id} not found in database.[/red]")
        raise typer.Exit(code=1)
        
    manager = workspace_service.workspace_manager
    try:
        archive_path = manager.archive_session(session.target_domain, job_id)
        console.print(f"[green]Successfully exported session to:[/green] {archive_path}")
    except FileNotFoundError as e:
        console.print(f"[red]{str(e)}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Failed to export session: {str(e)}[/red]")
        raise typer.Exit(code=1)


@app.command("inspect")
def inspect_cmd(job_id: str = typer.Argument(..., help="The Job ID to inspect")):
    """Aggregate and inspect persisted runtime data."""
    session = persistence_service.get_session(job_id)
    if not session:
        console.print(f"[red]Job {job_id} not found in database.[/red]")
        raise typer.Exit(code=1)
        
    console.print(Panel(f"[bold blue]Inspection for Job: {job_id}[/bold blue]\nTarget: {session.target_domain}\nStatus: {session.status}"))
    
    findings = persistence_service.get_findings_for_session(job_id)
    reports = persistence_service.get_reports_for_session(job_id)
    logs = persistence_service.get_logs_for_session(job_id)
    
    manager = workspace_service.workspace_manager
    session_dir = manager.get_session_dir(session.target_domain, job_id)
    
    # Render full operational dump
    console.print("\n[bold]1. Pipeline & Execution[/bold]")
    console.print("  Planner: [yellow]Unavailable[/yellow]")
    console.print("  Execution Plan: [yellow]Unavailable[/yellow]")
    console.print("  Node Execution: [yellow]Unavailable[/yellow]")
    
    console.print("\n[bold]2. Plugin & Wrapper Results[/bold]")
    console.print("  Wrapper Results: [yellow]Unavailable[/yellow]")
    console.print("  Plugin Results: [yellow]Unavailable[/yellow]")
    
    console.print("\n[bold]3. Execution State[/bold]")
    console.print("  Recon: [yellow]Unavailable[/yellow]")
    console.print("  JS: [yellow]Unavailable[/yellow]")
    console.print("  API: [yellow]Unavailable[/yellow]")
    console.print("  Vulnerability: [yellow]Unavailable[/yellow]")
    console.print("  Analysis: [yellow]Unavailable[/yellow]")
    
    console.print("\n[bold]4. Outputs & Workspace[/bold]")
    console.print(f"  Findings: {len(findings)}")
    console.print(f"  Reports: {len(reports)}")
    if session_dir.exists():
        console.print(f"  Workspace: {session_dir}")
        artifacts_dir = session_dir / "artifacts"
        if artifacts_dir.exists():
            console.print(f"  Artifacts: {len(list(artifacts_dir.iterdir()))}")
        else:
            console.print("  Artifacts: 0")
    else:
        console.print("  Workspace: [yellow]Unavailable[/yellow]")
        console.print("  Artifacts: [yellow]Unavailable[/yellow]")
        
    console.print("\n[bold]5. Telemetry & Analytics[/bold]")
    console.print("  Telemetry: [yellow]Persisted telemetry accessed via Analytics CLI[/yellow]")
    console.print("  Analytics: [yellow]Unavailable[/yellow]")
    console.print(f"  Logs: {len(logs)}")
    
    console.print("\n[bold]6. Metadata[/bold]")
    console.print(f"  Started At: {session.started_at}")
    console.print(f"  Finished At: {session.finished_at}")
    console.print("  Persistence Summary: OK")
