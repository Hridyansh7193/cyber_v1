import typer
from typing import Optional
from services.search_service import SearchService
from services.persistence_service import PersistenceService
from schemas.enums import SearchEntityType
from cli.output_formatter import OutputFormatter
from cli.decorators import timed_cli_command
from cli.exit_codes import SUCCESS, INTERNAL_ERROR, VALIDATION_ERROR

app = typer.Typer(help="Search operations across sessions and entities")

@app.command("search")
@timed_cli_command
def search(
    ctx: typer.Context,
    query: str = typer.Argument(..., help="Search query string"),
    type: Optional[SearchEntityType] = typer.Option(None, "--type", help="Specific entity type to search"),
    limit: int = typer.Option(50, "--limit", help="Maximum number of results"),
    offset: int = typer.Option(0, "--offset", "--page", help="Offset for pagination"),
    session: Optional[str] = typer.Option(None, "--session", help="Restrict to a specific session ID"),
    sort: str = typer.Option("relevance", "--sort", help="Sorting: relevance, newest, oldest"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format")
):
    if ctx.invoked_subcommand is not None:
        return

    if sort not in ("relevance", "newest", "oldest"):
        OutputFormatter.render_error("Invalid sort option.")
        raise typer.Exit(code=VALIDATION_ERROR)

    try:
        persistence = PersistenceService()
        search_service = SearchService(persistence)
        
        response = search_service.search(
            query=query,
            entity_type=type,
            limit=limit,
            offset=offset,
            session_id=session,
            sort=sort
        )

        if json_out:
            OutputFormatter.render(response, format="json")
        else:
            OutputFormatter.render_success(f"Found {response.total_matches} matches (showing {len(response.results)})")
            if response.results:
                headers = list(response.results[0].keys())[:4]  # Show max 4 cols
                rows = [[str(res.get(h, ""))[:50] for h in headers] for res in response.results]
                OutputFormatter.render_table(f"Search Results: {query}", headers, rows)
            
        raise typer.Exit(code=SUCCESS)
    except typer.Exit:
        raise
    except Exception as e:
        OutputFormatter.render_error(str(e))
        raise typer.Exit(code=INTERNAL_ERROR)
