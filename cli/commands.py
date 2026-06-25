import typer
from rich.console import Console
from rich.table import Table
import yaml
import json
from config.schemas import BugHunterConfig
from services.job_registry import JobRegistry
from services.orchestrator_adapter import OrchestratorAdapter
from services.scan_service import ScanService
from services.report_service import ReportService
from cli.progress import track_scan_progress

app = typer.Typer()
console = Console()

registry = JobRegistry()

def _create_default_config() -> BugHunterConfig:
    return BugHunterConfig(
        settings={"scan_depth": 1, "max_concurrency": 10, "log_level": "INFO"},
        llm={"provider": "dummy", "default_model": "dummy", "timeout": 30},
        tools={"tool_paths": {}, "docker_container_names": {}, "wordlists": {}, "enable_flags": {}},
        timeouts={"subfinder_timeout": 60, "nuclei_timeout": 60, "dalfox_timeout": 60, "ffuf_timeout": 60, "global_timeout": 3600},
        reporting={"report_formats": ["json"], "output_directories": {}}
    )

default_config = _create_default_config()
adapter = OrchestratorAdapter(registry, default_config)
scan_service = ScanService(adapter, registry)
report_service = ReportService(adapter)

@app.command("scan")
def scan_cmd(domain: str, config: str = typer.Option(None, help="Path to config file")):
    """Start a new scan."""
    cfg = default_config
    if config:
        with open(config, "r") as f:
            if config.endswith(".json"):
                cfg = BugHunterConfig.model_validate(json.load(f))
            else:
                cfg = BugHunterConfig.model_validate(yaml.safe_load(f))
                
    try:
        job_id = scan_service.submit_scan(domain, cfg)
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
    for k, v in status_info.items():
        table.add_row(k, str(v))
    console.print(table)

@app.command("report")
def report_cmd(job_id: str, format: str = typer.Option("json", help="Format: json or markdown")):
    """Get the report for a job."""
    rep = report_service.get_report(job_id, format)
    if not rep:
        console.print("[red]Report not found or not yet generated.[/red]")
        raise typer.Exit(code=1)
    console.print(rep.content)

@app.command("cancel")
def cancel_cmd(job_id: str):
    """Cancel a running job."""
    success = scan_service.cancel_scan(job_id)
    if success:
        console.print(f"[green]Job {job_id} cancelled.[/green]")
    else:
        console.print(f"[red]Job {job_id} could not be cancelled (might not exist or already finished).[/red]")

@app.command("list-jobs")
def list_jobs_cmd():
    """List all transient jobs."""
    jobs = registry.get_all_jobs()
    if not jobs:
        console.print("No jobs found in current session.")
        return
        
    table = Table("Job ID", "Target", "Status", "Progress")
    for job in jobs:
        table.add_row(job.job_id, job.target_domain, job.status.value, f"{job.progress:.1f}%")
    console.print(table)

@app.command("validate-config")
def validate_config_cmd(config_path: str):
    """Validate a configuration file."""
    try:
        with open(config_path, "r") as f:
            if config_path.endswith(".json"):
                BugHunterConfig.model_validate(json.load(f))
            else:
                BugHunterConfig.model_validate(yaml.safe_load(f))
        console.print("[green]Configuration is valid.[/green]")
    except ValueError as e:
        console.print(f"[red]Invalid configuration:[/red] {e}")
        raise typer.Exit(code=2)
    except Exception as e:
        # Top-level CLI catch to prevent ugly stack traces from leaking to the user's terminal
        import logging
        logging.getLogger(__name__).error("Unexpected CLI error", exc_info=True)
        console.print(f"[red]Unexpected Error:[/red] {e}")
        raise typer.Exit(code=1)

@app.command("version")
def version_cmd():
    """Show the application version."""
    console.print("BugHunter v0.1.0")
