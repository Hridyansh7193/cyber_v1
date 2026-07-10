import typer
from services.persistence_service import PersistenceService
from schemas.cli_responses import PlannerResponse
from cli.output_formatter import OutputFormatter
from cli.decorators import timed_cli_command
from cli.exit_codes import SUCCESS, NOT_FOUND, INTERNAL_ERROR

app = typer.Typer(help="Planner diagnostics")

@app.callback(invoke_without_command=True)
@timed_cli_command
def planner(
    ctx: typer.Context,
    job_id: str = typer.Argument(..., help="Session JOB_ID"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format")
):
    if ctx.invoked_subcommand is not None:
        return

    try:
        persistence = PersistenceService()
        tasks = persistence.get_task_queue(job_id)
        
        if tasks is None:
            OutputFormatter.render_error(f"Task Queue not found for JOB_ID {job_id}")
            raise typer.Exit(code=NOT_FOUND)
            
        response = PlannerResponse(
            planner_version="1.0",
            task_queue=tasks,
            total_tasks=len(tasks)
        )

        if json_out:
            OutputFormatter.render(response, format="json")
        else:
            OutputFormatter.render_tree(
                f"Planner Decision for {job_id}", 
                response.model_dump()
            )
            
        raise typer.Exit(code=SUCCESS)
    except typer.Exit:
        raise
    except Exception as e:
        OutputFormatter.render_error(str(e))
        raise typer.Exit(code=INTERNAL_ERROR)
