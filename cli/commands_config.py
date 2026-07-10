import typer
import yaml
from config.loader import load_config
from cli.output_formatter import OutputFormatter
from cli.decorators import timed_cli_command
from cli.exit_codes import SUCCESS, INTERNAL_ERROR, CONFIG_ERROR
from pathlib import Path

app = typer.Typer(help="Configuration management")

@app.command("show")
@timed_cli_command
def show_cmd(
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format")
):
    try:
        cfg = load_config()
        cfg_dict = cfg.model_dump()
        if json_out:
            OutputFormatter.render(cfg.model_dump(), format="json")
        else:
            OutputFormatter.render_tree("Active Configuration", cfg_dict)
        raise typer.Exit(code=SUCCESS)
    except typer.Exit:
        raise
    except Exception as e:
        OutputFormatter.render_error(str(e))
        raise typer.Exit(code=INTERNAL_ERROR)

@app.command("dump")
@timed_cli_command
def dump_cmd(
    format: str = typer.Option("yaml", "--format", help="Format to dump (yaml|json)")
):
    try:
        cfg = load_config()
        if format == "json":
            OutputFormatter.render(cfg.model_dump(), format="json")
        elif format == "yaml":
            yaml_str = yaml.safe_dump(
            cfg.model_dump(),
            sort_keys=False,
            default_flow_style=False,
        )       
            OutputFormatter.render_success(yaml_str)
        else:
            OutputFormatter.render_error(f"Unsupported format: {format}")
            raise typer.Exit(code=CONFIG_ERROR)
        raise typer.Exit(code=SUCCESS)
    except typer.Exit:
        raise
    except Exception as e:
        OutputFormatter.render_error(str(e))
        raise typer.Exit(code=INTERNAL_ERROR)

@app.command("validate")
@timed_cli_command
def validate_cmd(
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format")
):
    try:
        # If this succeeds, the configuration is valid.
        load_config()

        result = {
            "status": "valid",
            "message": "Configuration is valid."
        }

        if json_out:
            OutputFormatter.render(result, format="json")
        else:
            OutputFormatter.render_success(result["message"])

        raise typer.Exit(code=SUCCESS)

    except typer.Exit:
        raise

    except Exception as e:
        OutputFormatter.render_error(str(e))
        raise typer.Exit(code=CONFIG_ERROR)

@app.command("doctor")
@timed_cli_command
def doctor_cmd(
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format")
):
    # For now simply delegate to validate
    validate_cmd(json_out=json_out)

@app.command("diff")
@timed_cli_command
def diff_cmd(
    target1: str = typer.Argument(None, help="First profile/file"),
    target2: str = typer.Argument(None, help="Second profile/file"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format")
):
    try:
        import difflib
        
        def load_cfg(tgt):
            if not tgt: return load_config()
            if tgt.endswith(".yaml") or tgt.endswith(".yml"):
                with open(tgt, "r") as f:
                    return yaml.safe_load(f)
            # Otherwise assume profile name
            profile_path = Path(f"config/scan_profiles/default/{tgt}.yaml")
            if profile_path.exists():
                with open(profile_path, "r") as f:
                    return yaml.safe_load(f)
            raise ValueError(f"Profile or file not found: {tgt}")

        cfg1 = load_cfg(target1)
        cfg2 = load_cfg(target2)
        
        if hasattr(cfg1, "model_dump"):
            cfg1 = cfg1.model_dump()

        if hasattr(cfg2, "model_dump"):
            cfg2 = cfg2.model_dump()
        str1 = json_lib.dumps(cfg1, indent=2).splitlines()
        str2 = json_lib.dumps(cfg2, indent=2).splitlines()
        
        diff = list(difflib.unified_diff(str1, str2, lineterm=""))
        
        if json_out:
            OutputFormatter.render({"diff": diff}, format="json")
        else:
            if diff:
                for line in diff:
                    OutputFormatter.render_success(line)
            else:
                OutputFormatter.render_success("No differences found.")
        raise typer.Exit(code=SUCCESS)
    except typer.Exit:
        raise
    except Exception as e:
        OutputFormatter.render_error(str(e))
        raise typer.Exit(code=CONFIG_ERROR)
