import typer
from rich.console import Console
from rich.table import Table
from cli.dependencies import registry, scan_service, persistence_service, default_config
from cli.progress import track_scan_progress

app = typer.Typer(help="Job Lifecycle Management")
console = Console()

@app.command("jobs")
def jobs_cmd():
    """List all transient and persisted jobs."""
    jobs = registry.get_all_jobs()
    sessions = []
    if persistence_service:
        sessions = persistence_service.get_all_sessions()
        
    if not jobs and not sessions:
        console.print("No jobs found in current session or database.")
        return
        
    table = Table("Job ID", "Target", "Status", "Progress/Started")
    seen = set()
    
    for job in jobs:
        table.add_row(job.job_id, job.target_domain, job.status.value, f"{job.progress:.1f}%")
        seen.add(job.job_id)
        
    for s in sessions:
        if s.session_id not in seen:
            table.add_row(s.session_id, s.target_domain, s.status, str(s.started_at))
            seen.add(s.session_id)
            
    console.print(table)

@app.command("status")
def status_cmd(job_id: str):
    """Get the status of a job."""
    status_info = scan_service.get_status(job_id)
    if not status_info:
        console.print("[red]Job not found.[/red]")
        raise typer.Exit(code=1)
        
    table = Table(title=f"Status for {job_id}")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="magenta")
    
    # Format keys nicely and ensure workspace path, report count, finding count are shown
    for k, v in status_info.items():
        table.add_row(k.replace("_", " ").title(), str(v))
        
    console.print(table)

@app.command("cancel")
def cancel_cmd(job_id: str):
    """Cancel a running job."""
    success = scan_service.cancel_scan(job_id)
    if success:
        console.print(f"[green]Job {job_id} cancelled.[/green]")
    else:
        console.print(f"[red]Job {job_id} could not be cancelled (might not exist or already finished).[/red]")

@app.command("rerun")
def rerun_cmd(job_id: str):
    """Rerun a previous scan."""
    if not persistence_service:
        console.print("[red]Persistence not available.[/red]")
        raise typer.Exit(code=1)
        
    session = persistence_service.get_session(job_id)
    if not session:
        console.print("[red]Job not found.[/red]")
        raise typer.Exit(code=1)
        
    console.print(f"[green]Rerunning scan for {session.target_domain}[/green]")
    try:
        new_job_id = scan_service.submit_scan(session.target_domain, default_config)
        console.print(f"[green]Scan submitted![/green] New Job ID: [bold]{new_job_id}[/bold]")
        track_scan_progress(scan_service, new_job_id)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)

@app.command("resume")
def resume_cmd(job_id: str):
    """Resume an interrupted scan."""
    console.print("[yellow]Resume is not yet supported for this checkpoint.[/yellow]")
    # Exit cleanly as requested
    raise typer.Exit(code=0)
