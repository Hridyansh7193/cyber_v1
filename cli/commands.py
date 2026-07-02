import typer
from rich.console import Console
import yaml
import json
from config.schemas import BugHunterConfig
from cli.dependencies import adapter, registry, persistence_service, report_service, scan_service, workspace_service, default_config
from cli.progress import track_scan_progress

app = typer.Typer()
console = Console()

@app.command("scan")
def scan_cmd(
    domain: str, 
    config: str = typer.Option(None, help="Path to config file"),
    header: list[str] = typer.Option(None, "--header", "-H", help="Custom headers (e.g. 'Cookie: session=123')"),
    resume: str = typer.Option(None, "--resume", help="Resume an interrupted scan given its session ID")
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
                
    try:
        job_id = scan_service.submit_scan(domain, cfg, resume_session_id=resume)
        console.print(f"[green]Scan submitted![/green] Job ID: [bold]{job_id}[/bold]")
        track_scan_progress(scan_service, job_id)
        
        status = scan_service.get_status(job_id)
        if status and status["status"] == "failed":
            console.print(f"[red]Scan failed:[/red] {status.get('error')}")
            raise typer.Exit(code=1)
            
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
