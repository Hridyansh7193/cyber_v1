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
    console.print(f"[bold cyan]Findings:[/bold cyan] {len(findings)}")
    
    reports = persistence_service.get_reports_for_session(job_id)
    console.print(f"[bold cyan]Reports:[/bold cyan] {len(reports)}")
    
    logs = persistence_service.get_logs_for_session(job_id)
    console.print(f"[bold cyan]Logs:[/bold cyan] {len(logs)}")
    
    manager = workspace_service.workspace_manager
    session_dir = manager.get_session_dir(session.target_domain, job_id)
    if session_dir.exists():
        console.print(f"[bold cyan]Workspace Path:[/bold cyan] {session_dir}")
    else:
        console.print("[yellow]Workspace Path: UNAVAILABLE[/yellow]")
        
    console.print("[yellow]Planner Data: Persisted data not available via DB currently.[/yellow]")
    console.print("[yellow]Telemetry Data: Persisted telemetry accessed via Analytics CLI.[/yellow]")
