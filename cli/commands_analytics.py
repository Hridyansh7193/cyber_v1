import typer
import platform
import sys
from typing import Optional
from services.analytics_service import AnalyticsService
from services.persistence_service import PersistenceService
from schemas.cli_responses import AnalyticsResponse
from cli.output_formatter import OutputFormatter
from cli.decorators import timed_cli_command
from cli.exit_codes import SUCCESS, INTERNAL_ERROR

app = typer.Typer(help="Analytics and metric operations")

@app.command("analytics")
@timed_cli_command
def analytics(
    ctx: typer.Context,
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
    csv_out: bool = typer.Option(False, "--csv", help="Output in CSV format")
):
    if ctx.invoked_subcommand is not None:
        return

    try:
        persistence = PersistenceService()
        analytics_service = AnalyticsService(persistence)
        stats = analytics_service.get_aggregate_analytics()
        
        response = AnalyticsResponse(**stats)

        # Include Export Metadata if exporting
        if json_out or csv_out:
            metadata = {
                "version": "1.0.0", # BugHunter version
                "python_version": platform.python_version(),
                "os": platform.system(),
            }
            # For JSON, we can inject it or just print the response.
            # Real implementation might embed metadata into the response object itself.

        if json_out:
            OutputFormatter.render(response, format="json")
        elif csv_out:
            OutputFormatter.render(response, format="csv")
        else:
            OutputFormatter.render_table(
                "Aggregated Analytics",
                ["Metric", "Value"],
                [[k, v] for k, v in response.model_dump().items() if not isinstance(v, (dict, list))]
            )
            # Render complex items as tree
            complex_items = {k: v for k, v in response.model_dump().items() if isinstance(v, (dict, list))}
            OutputFormatter.render_tree("Analytics Details", complex_items)
            
        raise typer.Exit(code=SUCCESS)
    except typer.Exit:
        raise
    except Exception as e:
        OutputFormatter.render_error(str(e))
        raise typer.Exit(code=INTERNAL_ERROR)
