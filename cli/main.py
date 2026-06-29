import typer
import sys
import logging
from cli.version import __version__
from cli.commands import app as legacy_app
from cli.commands_jobs import app as jobs_app
from cli.commands_workspace import app as workspace_app
from cli.commands_report import app as report_app
from cli.commands_logs import app as logs_app
from cli.commands_search import app as search_app
from cli.commands_config import app as config_app
from cli.commands_profile import app as profile_app
from cli.commands_analytics import app as analytics_app
from cli.commands_planner import app as planner_app
from cli.commands_artifacts import app as artifacts_app
from cli.commands_doctor import app as doctor_app

def version_callback(value: bool):
    if value:
        from rich.console import Console
        console = Console()
        console.print(f"BugHunter v{__version__}")
        raise typer.Exit()

app = typer.Typer(help="BugHunter CLI")

@app.callback()
def main_callback(
    version: bool = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True, help="Show the application version and exit."
    ),
    verbose: bool = typer.Option(False, "--verbose", help="Enable verbose logging"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging")
):
    """BugHunter CLI Application."""
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    elif verbose:
        logging.getLogger().setLevel(logging.INFO)

# Attach sub-apps
app.add_typer(jobs_app, name="") # Mount job commands at top level to preserve `jobs`, `status`
app.add_typer(doctor_app, name="") # Mount doctor, plugins, verify, self-test at top level
app.add_typer(workspace_app, name="workspace", help="Workspace commands")
app.add_typer(report_app, name="")
app.add_typer(logs_app, name="logs", help="Logs commands")
app.add_typer(search_app, name="search", help="Search commands")
app.add_typer(config_app, name="config", help="Configuration commands")
app.add_typer(profile_app, name="profile", help="Profile commands")
app.add_typer(analytics_app, name="analytics", help="Analytics commands")
app.add_typer(planner_app, name="planner", help="Planner commands")
app.add_typer(artifacts_app, name="artifacts", help="Artifact commands")

# Ensure legacy commands (scan, validate-config) are still accessible at root
app.add_typer(legacy_app, name="")

def main():
    app()

if __name__ == "__main__":
    main()
