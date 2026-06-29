import typer
import json
from services.persistence_service import PersistenceService
from cli.output_formatter import OutputFormatter
from cli.decorators import timed_cli_command
from cli.exit_codes import SUCCESS, NOT_FOUND, INTERNAL_ERROR

app = typer.Typer(help="Logs and telemetry diagnostics")

@app.command("logs")
@timed_cli_command
def logs_cmd(
    job_id: str = typer.Argument(..., help="Session JOB_ID"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format")
):
    try:
        persistence = PersistenceService()
        logs = persistence.get_logs_for_session(job_id)
        
        if not logs:
            OutputFormatter.render_error(f"No logs found for JOB_ID {job_id}")
            raise typer.Exit(code=NOT_FOUND)
            
        data = []
        for l in logs:
            data.append({
                "timestamp": l.timestamp,
                "level": l.level,
                "node": l.node,
                "message": l.message
            })

        if json_out:
            OutputFormatter.render(data, format="json")
        else:
            OutputFormatter.render_table(
                f"Execution Logs: {job_id}",
                ["Timestamp", "Level", "Node", "Message"],
                [[d["timestamp"], d["level"], d["node"], d["message"][:100]] for d in data]
            )
            
        raise typer.Exit(code=SUCCESS)
    except typer.Exit:
        raise
    except Exception as e:
        OutputFormatter.render_error(str(e))
        raise typer.Exit(code=INTERNAL_ERROR)

@app.command("telemetry")
@timed_cli_command
def telemetry(
    job_id: str = typer.Argument(..., help="Session JOB_ID"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format")
):
    try:
        persistence = PersistenceService()
        logs = persistence.get_logs_for_session(job_id)
        
        if not logs:
            OutputFormatter.render_error(f"No telemetry found for JOB_ID {job_id}")
            raise typer.Exit(code=NOT_FOUND)
            
        telemetry_data = []
        for l in logs:
            if l.details:
                try:
                    details = json.loads(l.details)
                    if details.get("type") == "tool_telemetry":
                        telemetry_data.append({
                            "Tool": details.get("tool_name", ""),
                            "Resolved Binary Path": details.get("binary_path", "unknown"),
                            "Command": details.get("command", ""),
                            "Arguments": details.get("args", ""),
                            "Exit Code": details.get("exit_code", 0),
                            "Duration": details.get("duration", 0.0),
                            "Started": details.get("start_time", ""),
                            "Finished": details.get("end_time", ""),
                            "Stdout bytes": details.get("stdout_bytes", 0),
                            "Stderr bytes": details.get("stderr_bytes", 0),
                            "Success": details.get("success", False),
                            "Timeout": details.get("timeout", False),
                            "Retries": details.get("retries", 0)
                        })
                except json.JSONDecodeError:
                    pass

        if json_out:
            OutputFormatter.render(telemetry_data, format="json")
        else:
            if not telemetry_data:
                OutputFormatter.render_error(f"No tool telemetry found in logs for JOB_ID {job_id}")
                raise typer.Exit(code=NOT_FOUND)
                
            headers = list(telemetry_data[0].keys())
            rows = [[str(d.get(h, "")) for h in headers] for d in telemetry_data]
            OutputFormatter.render_table(f"Telemetry: {job_id}", headers, rows)
            
        raise typer.Exit(code=SUCCESS)
    except typer.Exit:
        raise
    except Exception as e:
        OutputFormatter.render_error(str(e))
        raise typer.Exit(code=INTERNAL_ERROR)
