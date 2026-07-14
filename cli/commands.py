import typer
from rich.console import Console
import yaml
import json
from config.schemas import BugHunterConfig
from cli.dependencies import scan_service, default_config
from cli.progress import track_scan_progress

app = typer.Typer()
console = Console()

@app.command("scan")
def scan_cmd(
    domain: str, 
    config: str = typer.Option(None, help="Path to config file"),
    header: list[str] = typer.Option(None, "--header", "-H", help="Custom headers (e.g. 'Cookie: session=123')"),
    resume: str = typer.Option(None, "--resume", help="Resume an interrupted scan given its session ID"),
    profile: str = typer.Option("balanced", "--profile", help="Performance profile (light, balanced, aggressive, custom)")
):
    """Start a new scan or resume an interrupted one."""
    cfg = default_config
    if config:
        with open(config, "r") as f:
            if config.endswith(".json"):
                cfg = BugHunterConfig.model_validate(json.load(f))
            else:
                cfg = BugHunterConfig.model_validate(yaml.safe_load(f))
                
    if header:
        # Pydantic models with frozen=True require model_copy(update=...)
        new_auth = cfg.auth.model_copy(update={"headers": list(header)})
        cfg = cfg.model_copy(update={"auth": new_auth})
        
    if profile:
        from config.schemas import PerformanceProfile
        try:
            profile_enum = PerformanceProfile(profile.lower())
            cfg = cfg.model_copy(update={"profile": profile_enum})
        except ValueError:
            console.print(f"[red]Invalid profile:[/red] {profile}. Valid options: light, balanced, aggressive, custom")
            raise typer.Exit(code=2)
                
    try:
        job_id = scan_service.submit_scan(domain, cfg, resume_session_id=resume)
        console.print(f"[green]Scan submitted![/green] Job ID: [bold]{job_id}[/bold]")
        track_scan_progress(scan_service, job_id)
        
        status = scan_service.get_status(job_id)
        if status and status["status"] == "failed":
            console.print(f"[red]Scan failed:[/red] {status.get('error')}")
            raise typer.Exit(code=1)
            
        from cli.dashboard import render_final_dashboard
        render_final_dashboard(job_id)
        
        from cli.dependencies import workspace_service
        manager = workspace_service.workspace_manager
        from services.target_service import TargetService
        normalized_target = TargetService.normalize_target(domain, job_id).domain
        session_dir = manager.get_session_dir(normalized_target, job_id)
        reports_dir = session_dir / "reports"
        
        console.print("\n[bold]Reports Generated:[/bold]")
        console.print(f"  [cyan]Markdown:[/cyan] {reports_dir / 'report.md'}")
        console.print(f"  [cyan]JSON:[/cyan]     {reports_dir / 'report.json'}")
        console.print(f"  [cyan]SARIF:[/cyan]    {reports_dir / 'report.sarif'}")
        console.print(f"  [cyan]Workspace:[/cyan] {session_dir}")
            
    except ValueError as e:
        console.print(f"[red]Validation Error:[/red] {e}")
        raise typer.Exit(code=2)
    except Exception as e:
        # Top-level CLI catch to prevent ugly stack traces from leaking to the user's terminal
        import logging
        logging.getLogger(__name__).error("Unexpected CLI error", exc_info=True)
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)

@app.command("version")
def version_cmd():
    """Show the application version."""
    console.print("BugHunter v0.1.0")

@app.command("report")
def report_cmd(
    job_id: str,
    format: str = typer.Option("json", "--format", "-f", help="Report format to display (json, md, sarif)"),
    show: bool = typer.Option(False, "--show", help="Print the report content to stdout")
):
    """Locate and optionally display a finalized scan report."""
    status = scan_service.get_status(job_id)
    if not status:
        console.print(f"[red]Error:[/red] Job ID not found: {job_id}")
        raise typer.Exit(code=1)
        
    domain = status.get("target")
    if not domain:
        console.print(f"[red]Error:[/red] Job target not found for job: {job_id}")
        raise typer.Exit(code=1)
        
    from services.target_service import TargetService
    try:
        normalized_domain = TargetService.normalize_target(domain, job_id).domain
    except Exception:
        normalized_domain = domain
        
    from cli.dependencies import workspace_service
    manager = workspace_service.workspace_manager
    session_dir = manager.get_session_dir(normalized_domain, job_id)
    reports_dir = session_dir / "reports"
    
    # Map 'md' to 'markdown' if needed by some internals, but file is report.md
    file_ext = "md" if format.lower() == "markdown" else format.lower()
    report_file = reports_dir / f"report.{file_ext}"
    
    if not report_file.exists():
        console.print(f"[yellow]Warning:[/yellow] Report file not found at {report_file}")
        # Try finding it via get_report as fallback
        generated = scan_service.get_report(job_id, format)
        if not generated:
            console.print("[red]Error:[/red] Report content could not be found or loaded.")
            raise typer.Exit(code=1)
        else:
            if show:
                console.print(generated.content)
            else:
                console.print("[green]Report generated but not saved to disk workspace.[/green] Use --show to view.")
        return
        
    if show:
        try:
            with open(report_file, "r", encoding="utf-8") as f:
                content = f.read()
            if format.lower() in ("md", "markdown"):
                from rich.markdown import Markdown
                console.print(Markdown(content))
            elif format.lower() == "json":
                from rich.syntax import Syntax
                console.print(Syntax(content, "json", theme="monokai"))
            else:
                console.print(content)
        except Exception as e:
            console.print(f"[red]Error reading report:[/red] {e}")
            raise typer.Exit(code=1)
    else:
        import os
        console.print(f"[bold]Canonical Report Path:[/bold] {os.path.abspath(report_file)}")

