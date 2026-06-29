import typer
import os
from datetime import datetime, UTC
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from cli.dependencies import workspace_service, persistence_service

app = typer.Typer(help="Manage local workspace, sessions, and artifacts.")
console = Console()

@app.command("list")
def list_cmd(target: Optional[str] = typer.Option(None, "--target", "-t", help="Filter by target domain")):
    """List all workspace sessions."""
    sessions = persistence_service.get_all_sessions()
    
    if target:
        sessions = [s for s in sessions if s.target_domain == target]
        
    if not sessions:
        console.print("[yellow]No sessions found in the database.[/yellow]")
        raise typer.Exit()
        
    table = Table(title="Workspace Sessions")
    table.add_column("Session ID", style="cyan")
    table.add_column("Target", style="magenta")
    table.add_column("Status", style="blue")
    table.add_column("Started At", style="green")
    
    # Sort by started_at descending
    sessions.sort(key=lambda s: s.started_at if s.started_at else datetime.now(UTC), reverse=True)
    
    for s in sessions:
        table.add_row(s.session_id, s.target_domain, s.status, str(s.started_at))
        
    console.print(table)


@app.command("stats")
def stats_cmd():
    """Show workspace statistics (counts, sizes)."""
    manager = workspace_service.workspace_manager
    stats = manager.get_workspace_stats()
    
    table = Table(title="Workspace Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    
    table.add_row("Targets", str(stats["targets"]))
    table.add_row("Sessions", str(stats["sessions"]))
    table.add_row("Generated Reports", str(stats["reports"]))
    table.add_row("Log Files", str(stats["logs"]))
    
    size_mb = stats["total_size_bytes"] / (1024 * 1024)
    table.add_row("Total Size", f"{size_mb:.2f} MB")
    
    console.print(table)


@app.command("browse")
def browse_cmd(job_id: str = typer.Argument(..., help="The Job ID (Session ID) to browse")):
    """List all artifacts and files within a specific session."""
    session_model = persistence_service.get_session(job_id)
    if not session_model:
        console.print(f"[red]Job {job_id} not found in database.[/red]")
        raise typer.Exit(code=1)
        
    manager = workspace_service.workspace_manager
    session_dir = manager.get_session_dir(session_model.target_domain, job_id)
    
    if not session_dir.exists():
        console.print(f"[red]Workspace directory not found for job {job_id}.[/red]")
        raise typer.Exit(code=1)
        
    tree = Tree(f"[bold blue]{session_model.target_domain} / {job_id}[/bold blue]")
    
    def add_directory_to_tree(directory, tree_node):
        for item in sorted(os.listdir(directory)):
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path):
                branch = tree_node.add(f"[bold cyan]{item}/[/bold cyan]")
                add_directory_to_tree(item_path, branch)
            else:
                tree_node.add(f"{item}")
                
    add_directory_to_tree(session_dir, tree)
    console.print(tree)


@app.command("archive")
def archive_cmd(job_id: str = typer.Argument(..., help="The Job ID to archive")):
    """Archive a session directory into a ZIP file."""
    session_model = persistence_service.get_session(job_id)
    if not session_model:
        console.print(f"[red]Job {job_id} not found in database.[/red]")
        raise typer.Exit(code=1)
        
    manager = workspace_service.workspace_manager
    try:
        archive_path = manager.archive_session(session_model.target_domain, job_id)
        console.print(f"[green]Successfully archived session to:[/green] {archive_path}")
    except FileNotFoundError as e:
        console.print(f"[red]{str(e)}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Failed to archive session: {str(e)}[/red]")
        raise typer.Exit(code=1)


@app.command("clean")
def clean_cmd():
    """Remove temporary and cache data from the workspace."""
    manager = workspace_service.workspace_manager
    try:
        manager.clean_temp()
        console.print("[green]Successfully cleaned temporary workspace data.[/green]")
    except Exception as e:
        console.print(f"[red]Failed to clean temp data: {str(e)}[/red]")
        raise typer.Exit(code=1)
