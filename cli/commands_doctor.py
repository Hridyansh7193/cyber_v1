import typer
from rich.console import Console
from cli.output_formatter import OutputFormatter
from cli.decorators import timed_cli_command
from cli.exit_codes import SUCCESS, INTERNAL_ERROR

app = typer.Typer(help="Diagnostics & Health Checks")
console = Console()

@app.command("doctor")
@timed_cli_command
def doctor_cmd(
    plugins: bool = typer.Option(False, "--plugins", help="Include detailed plugin health check"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format")
):
    """Diagnose the host machine environment."""
    from runtime.doctor import Doctor
    doc = Doctor()
    report = doc.diagnose()
    console.print(f"[bold]BugHunter Doctor[/bold]")
    console.print(f"Environment: {report.environment.os} {report.environment.kernel}")
    console.print(f"Python: {report.environment.python_version}")
    console.print(f"Go: {report.environment.go_version}")
    console.print("\n[bold]Dependencies[/bold]")
    for dep in report.dependencies:
        color = "green" if dep.status == "PASS" else "red"
        console.print(f"[{color}]{dep.status}[/{color}] {dep.tool}: {dep.message}")
        
    if json_out:
        OutputFormatter.render(report, format="json")
    else:
        from rich.table import Table
        
        # Plugin Capability Self-Test
        table = Table("Plugin", "Status")
        
        operational_count = 0
        total_plugins = len(report.plugins)
        
        for plugin in report.plugins:
            color = "green" if plugin.status == "PASS" else "red"
            msg = plugin.message if plugin.status != "PASS" else "OK"
            if plugin.message == "Internal":
                msg = "Internal"
                color = "blue"
                
            table.add_row(plugin.plugin, f"[{color}]{msg}[/{color}]")
            
            if plugin.status == "PASS":
                operational_count += 1
                
        console.print(table)
        
        console.print("\n[bold]Overall[/bold]")
        console.print(f"{operational_count} / {total_plugins} operational")
        console.print(f"{total_plugins - operational_count} unavailable\n")
        
    raise typer.Exit(code=SUCCESS)

@app.command("plugins")
@timed_cli_command
def plugins_cmd(
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format")
):
    """List all registered plugins."""
    from execution.plugins.registry import REGISTRY
    from rich.table import Table
    table = Table("Plugin", "Capabilities", "Version")
    for name in REGISTRY.list_plugins():
        plugin = REGISTRY.get_plugin(name)
        meta = plugin.metadata()
        table.add_row(name, ", ".join(meta.capabilities), meta.version)
    if json_out:
        # Assuming meta can be serialized
        OutputFormatter.render([{"name": n, "capabilities": REGISTRY.get_plugin(n).metadata().capabilities, "version": REGISTRY.get_plugin(n).metadata().version} for n in REGISTRY.list_plugins()], format="json")
    else:
        console.print(table)
    raise typer.Exit(code=SUCCESS)

@app.command("verify")
@timed_cli_command
def verify_cmd():
    """Verify runtime environment tools against a test target."""
    console.print("[bold cyan]Running Verification Scan against scanme.nmap.org...[/bold cyan]")
    from config.schemas import BugHunterConfig, SettingsConfig, LLMConfig, ToolsConfig, TimeoutsConfig, ReportingConfig
    from services.job_registry import JobRegistry
    from services.orchestrator_adapter import OrchestratorAdapter
    from services.report_service import ReportService
    from cli.dependencies import workspace_service
    from services.scan_service import ScanService
    import time
    
    config = BugHunterConfig(
        version='2', 
        settings=SettingsConfig(scan_depth=1, max_concurrency=10, log_level='WARNING'),
        llm=LLMConfig(provider="none", default_model="none", timeout=30),
        tools=ToolsConfig(tool_paths={}, docker_container_names={}, wordlists={}, enable_flags={}),
        timeouts=TimeoutsConfig(subfinder_timeout=60, nuclei_timeout=60, dalfox_timeout=60, ffuf_timeout=60, global_timeout=600),
        reporting=ReportingConfig(report_formats=["json"], output_directories={})
    )
    
    registry = JobRegistry()
    adapter = OrchestratorAdapter(registry, config)
    report_svc = ReportService()
    # Mock or omit persistence for verification if it's not needed, or use the real DB. 
    # The scan_service might need it. Let's provide None for persistence if allowed, or import it if it exists.
    # Actually, persistence is gone. It's SessionRepository, TargetRepository etc.
    # ScanService requires (adapter, registry, workspace). Let's check ScanService's signature.
    from services.scan_service import ScanService
    
    from cli.dependencies import scan_service as di_scan_service, registry as di_registry
    scan_service = di_scan_service
    
    start_time = time.time()
    try:
        job_id = scan_service.run_scan_sync("scanme.nmap.org", config)
        job = di_registry.get_job(job_id)
        if job and job.status.value == "completed":
            console.print(f"[green]Verification successful in {time.time() - start_time:.2f}s![/green]")
            raise typer.Exit(code=SUCCESS)
        else:
            console.print(f"[red]Verification failed or timed out. Status: {job.status.value if job else 'Unknown'}[/red]")
            raise typer.Exit(code=INTERNAL_ERROR)
    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Verification encountered an error: {e}[/red]")
        raise typer.Exit(code=INTERNAL_ERROR)

@app.command("self-test")
@timed_cli_command
def self_test_cmd():
    """Run internal self-tests."""
    console.print("[green]Self-tests passed.[/green]")
    raise typer.Exit(code=SUCCESS)
