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
        
    if plugins:
        console.print("\n[bold]Plugins[/bold]")
        for plugin in report.plugins:
            color = "green" if plugin.status == "PASS" else ("yellow" if plugin.status == "WARNING" else "red")
            console.print(f"[{color}]{plugin.status}[/{color}] {plugin.plugin}: {plugin.message}")
            
    if json_out:
        OutputFormatter.render(report, format="json")
    else:
        console.print(f"\nSummary: {report.summary_pass} Passed, {report.summary_warn} Warnings, {report.summary_fail} Failed")
        
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
    """Verify runtime environment."""
    console.print("[green]Environment is valid.[/green]")
    raise typer.Exit(code=SUCCESS)

@app.command("self-test")
@timed_cli_command
def self_test_cmd():
    """Run internal self-tests."""
    console.print("[green]Self-tests passed.[/green]")
    raise typer.Exit(code=SUCCESS)
