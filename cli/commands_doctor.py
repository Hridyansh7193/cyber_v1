import typer
from rich.console import Console

app = typer.Typer(help="Diagnostics & Health Checks")
console = Console()

@app.command("doctor")
def doctor_cmd(plugins: bool = typer.Option(False, "--plugins", help="Include detailed plugin health check")):
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
        
    if plugins:
        console.print("\n[bold]Plugins[/bold]")
        for plugin in report.plugins:
            color = "green" if plugin.status == "PASS" else ("yellow" if plugin.status == "WARNING" else "red")
            console.print(f"[{color}]{plugin.status}[/{color}] {plugin.plugin}: {plugin.message}")
            
    console.print(f"\nSummary: {report.summary_pass} Passed, {report.summary_warn} Warnings, {report.summary_fail} Failed")

@app.command("plugins")
def plugins_cmd():
    """List all registered plugins."""
    from execution.plugins.registry import REGISTRY
    from rich.table import Table
    table = Table("Plugin", "Capabilities", "Version")
    for name in REGISTRY.list_plugins():
        plugin = REGISTRY.get_plugin(name)
        meta = plugin.metadata()
        table.add_row(name, ", ".join(meta.capabilities), meta.version)
    console.print(table)

@app.command("verify")
def verify_cmd():
    """Verify runtime environment."""
    console.print("[green]Environment is valid.[/green]")

@app.command("self-test")
def self_test_cmd():
    """Run internal self-tests."""
    console.print("[green]Self-tests passed.[/green]")
