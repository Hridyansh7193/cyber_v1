import typer
import sys
import logging
from typing import Optional
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
from cli.commands_trace import app as trace_app

from cli.dependencies import workspace_service
from schemas.cli_responses import CleanupResponse
from cli.output_formatter import OutputFormatter
from cli.decorators import timed_cli_command
from cli.exit_codes import SUCCESS, INTERNAL_ERROR

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

@app.command("cleanup")
@timed_cli_command
def cleanup_cmd(
    force: bool = typer.Option(False, "--force", help="Actually perform deletion (default is dry-run)"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format")
):
    """Cleanup temporary data and cache. Defaults to dry-run unless --force is specified."""
    try:
        stats = workspace_service.perform_cleanup(force=force)
        response = CleanupResponse(**stats)
        
        if json_out:
            OutputFormatter.render(response, format="json")
        else:
            mode_str = " (DRY RUN)" if not force else ""
            OutputFormatter.render_table(
                f"Cleanup Statistics{mode_str}",
                ["Metric", "Value"],
                [[k, v] for k, v in response.model_dump().items()]
            )
            if not force:
                OutputFormatter.render_success("Run with --force to actually delete these files.")
                
        raise typer.Exit(code=SUCCESS)
    except typer.Exit:
        raise
    except Exception as e:
        OutputFormatter.render_error(str(e))
        raise typer.Exit(code=INTERNAL_ERROR)

# Attach sub-apps
app.add_typer(jobs_app, name="")
app.add_typer(doctor_app, name="")
app.add_typer(workspace_app, name="workspace", help="Workspace commands")
app.add_typer(report_app, name="")
app.add_typer(logs_app, name="logs", help="Logs commands")
app.add_typer(search_app, name="")
app.add_typer(config_app, name="config", help="Configuration commands")
app.add_typer(profile_app, name="profile", help="Profile commands")
app.add_typer(analytics_app, name="")
app.add_typer(planner_app, name="planner", help="Planner commands")
app.add_typer(artifacts_app, name="artifacts", help="Artifact commands")
app.add_typer(trace_app, name="")

# Ensure legacy commands (scan, validate-config) are still accessible at root
app.add_typer(legacy_app, name="")

def main():
    app()

if __name__ == "__main__":
    main()
