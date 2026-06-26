import typer
import sys
from rich.console import Console
from rich.table import Table
import yaml
import json
from config.schemas import BugHunterConfig
from services.job_registry import JobRegistry
from services.orchestrator_adapter import OrchestratorAdapter
from services.scan_service import ScanService
from services.report_service import ReportService
from services.runtime_service import RuntimeService
from cli.progress import track_scan_progress
from runtime.workspace import WorkspaceManager

app = typer.Typer()
console = Console()

registry = JobRegistry()
runtime_service = RuntimeService()
ws_manager = WorkspaceManager()

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
def scan_cmd(domain: str, config: str = typer.Option(None, help="Path to config file"), profile: str = typer.Option("bug_bounty", help="Scan profile to use")):
    """Start a new scan."""
    if not runtime_service.run_preflight(domain, profile):
        console.print("[red]Preflight validation failed.[/red]")
        sys.exit(6)
        
    cfg = default_config
    if config:
        try:
            with open(config, "r") as f:
                if config.endswith(".json"):
                    cfg = BugHunterConfig.model_validate(json.load(f))
                else:
                    cfg = BugHunterConfig.model_validate(yaml.safe_load(f))
        except Exception as e:
            console.print(f"[red]Config Error:[/red] {e}")
            sys.exit(3)
                
    try:
        job_id = scan_service.submit_scan(domain, cfg)
        console.print(f"[green]Scan submitted![/green] Job ID: [bold]{job_id}[/bold]")
        track_scan_progress(scan_service, job_id)
        
        status = scan_service.get_status(job_id)
        if status and status["status"] == "failed":
            console.print(f"[red]Scan failed:[/red] {status.get('error')}")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)

@app.command("doctor")
def doctor_cmd():
    """Diagnose the host machine environment."""
    report = runtime_service.run_doctor()
    console.print(f"[bold]Doctor Report[/bold]")
    for dep in report.dependencies:
        color = "green" if dep.status == "PASS" else ("yellow" if dep.status == "WARNING" else "red")
        console.print(f"[{color}]{dep.status}[/{color}]\t{dep.tool} ({dep.message})")
    
    for chk in report.checks:
        color = "green" if chk.status == "PASS" else ("yellow" if chk.status == "WARNING" else "red")
        console.print(f"[{color}]{chk.status}[/{color}]\t{chk.name}: {chk.message}")

    console.print(f"\nSummary: PASS {report.summary_pass}, WARN {report.summary_warn}, FAIL {report.summary_fail}")
    if report.summary_fail > 0:
        sys.exit(2)

@app.command("install")
def install_cmd(dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be installed")):
    """Install dependencies and templates."""
    summary = runtime_service.run_install(dry_run=dry_run)
    if dry_run:
        return
    if not summary.success:
        console.print("[red]Installation failed.[/red]")
        sys.exit(5)
    console.print("[green]Installation complete.[/green]")

@app.command("verify")
def verify_cmd():
    """Verify installation integrity."""
    report = runtime_service.run_verify()
    if report.summary_fail > 0:
        sys.exit(2)

@app.command("self-test")
def self_test_cmd():
    """Validate BugHunter internal components."""
    if not runtime_service.run_self_test():
        sys.exit(1)

@app.command("release-check")
def release_check_cmd():
    """Ultimate gate checking all systems."""
    if not runtime_service.run_release_check():
        console.print("[red]Release check FAIL[/red]")
        sys.exit(1)
    console.print("[green]READY[/green]")

@app.command("plugins")
def plugins_cmd():
    """Show plugin capability matrix."""
    from execution.plugins.registry import REGISTRY
    table = Table("Plugin", "Capabilities", "Status")
    for name in REGISTRY.list_plugins():
        plugin = REGISTRY.get_plugin(name)
        meta = plugin.metadata()
        status = "PASS" if plugin.health_check() else "FAIL"
        caps = ", ".join([c.value for c in meta.capabilities])
        table.add_row(name, caps, status)
    console.print(table)

@app.command("workspace")
def workspace_cmd(action: str = typer.Argument(..., help="list|clean|archive")):
    """Manage the BugHunter workspace."""
    if action == "list":
        sessions = ws_manager.list_sessions()
        table = Table("Session ID", "Target", "Profile", "Status")
        for s in sessions:
            table.add_row(s.session_id, s.target, s.profile, s.status)
        console.print(table)
    elif action == "clean":
        ws_manager.clean_temp()
        console.print("Workspace temporary files cleaned.")
    elif action == "archive":
        console.print("Provide a session ID to archive via `bughunter archive <id>`.")

@app.command("version")
def version_cmd():
    """Show detailed version info."""
    console.print("BugHunter v1.0.0")
    console.print("Config Schema: v2")
    console.print("Git Commit: latest")

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
    except Exception as e:
        console.print(f"[red]Invalid configuration:[/red] {e}")
        sys.exit(3)
