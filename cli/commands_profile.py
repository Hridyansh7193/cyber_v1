import typer
import yaml
import shutil
from pathlib import Path
from cli.output_formatter import OutputFormatter
from cli.decorators import timed_cli_command
from cli.exit_codes import SUCCESS, INTERNAL_ERROR, VALIDATION_ERROR, NOT_FOUND

app = typer.Typer(help="Profile management")

PROFILES_DIR = Path("config/scan_profiles/default")

@app.command("list")
@timed_cli_command
def list_cmd(
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format")
):
    try:
        if not PROFILES_DIR.exists():
            PROFILES_DIR.mkdir(parents=True)
            
        profiles = [p.stem for p in PROFILES_DIR.glob("*.yaml")]
        
        if json_out:
            OutputFormatter.render({"profiles": profiles}, format="json")
        else:
            OutputFormatter.render_table("Profiles", ["Profile Name"], [[p] for p in profiles])
        raise typer.Exit(code=SUCCESS)
    except typer.Exit:
        raise
    except Exception as e:
        OutputFormatter.render_error(str(e))
        raise typer.Exit(code=INTERNAL_ERROR)

@app.command("show")
@timed_cli_command
def show_cmd(
    name: str = typer.Argument(..., help="Profile name"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format")
):
    try:
        profile_path = PROFILES_DIR / f"{name}.yaml"
        if not profile_path.exists():
            OutputFormatter.render_error(f"Profile {name} not found.")
            raise typer.Exit(code=NOT_FOUND)
            
        with open(profile_path, "r") as f:
            cfg = yaml.safe_load(f)
            
        if json_out:
            OutputFormatter.render(cfg, format="json")
        else:
            OutputFormatter.render_tree(f"Profile: {name}", cfg)
        raise typer.Exit(code=SUCCESS)
    except typer.Exit:
        raise
    except Exception as e:
        OutputFormatter.render_error(str(e))
        raise typer.Exit(code=INTERNAL_ERROR)

@app.command("validate")
@timed_cli_command
def validate_cmd(
    name: str = typer.Argument(..., help="Profile name"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format")
):
    try:
        profile_path = PROFILES_DIR / f"{name}.yaml"
        if not profile_path.exists():
            OutputFormatter.render_error(f"Profile {name} not found.")
            raise typer.Exit(code=NOT_FOUND)
            
        with open(profile_path, "r") as f:
            cfg = yaml.safe_load(f)
            
        is_valid = isinstance(cfg, dict)
        
        result = {"status": "valid" if is_valid else "invalid", "message": f"Profile {name} is valid." if is_valid else "Profile invalid."}
        if json_out:
            OutputFormatter.render(result, format="json")
        else:
            if is_valid:
                OutputFormatter.render_success(result["message"])
            else:
                OutputFormatter.render_error(result["message"])
                
        raise typer.Exit(code=SUCCESS if is_valid else VALIDATION_ERROR)
    except typer.Exit:
        raise
    except Exception as e:
        OutputFormatter.render_error(str(e))
        raise typer.Exit(code=INTERNAL_ERROR)

@app.command("clone")
@timed_cli_command
def clone_cmd(
    source: str = typer.Argument(..., help="Source profile name"),
    name: str = typer.Option(..., "--name", help="New profile name"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format")
):
    try:
        src_path = PROFILES_DIR / f"{source}.yaml"
        dest_path = PROFILES_DIR / f"{name}.yaml"
        
        if not src_path.exists():
            OutputFormatter.render_error(f"Profile {source} not found.")
            raise typer.Exit(code=NOT_FOUND)
            
        if dest_path.exists():
            OutputFormatter.render_error(f"Profile {name} already exists.")
            raise typer.Exit(code=VALIDATION_ERROR)
            
        shutil.copy(src_path, dest_path)
        
        res = {"status": "success", "message": f"Cloned {source} to {name}"}
        if json_out:
            OutputFormatter.render(res, format="json")
        else:
            OutputFormatter.render_success(res["message"])
        raise typer.Exit(code=SUCCESS)
    except typer.Exit:
        raise
    except Exception as e:
        OutputFormatter.render_error(str(e))
        raise typer.Exit(code=INTERNAL_ERROR)

@app.command("create")
@timed_cli_command
def create_cmd(
    name: str = typer.Argument(..., help="New profile name"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format")
):
    try:
        dest_path = PROFILES_DIR / f"{name}.yaml"
        if dest_path.exists():
            OutputFormatter.render_error(f"Profile {name} already exists.")
            raise typer.Exit(code=VALIDATION_ERROR)
            
        with open(dest_path, "w") as f:
            yaml.dump({"execution": {"mode": "auto"}}, f)
            
        res = {"status": "success", "message": f"Created profile {name}"}
        if json_out:
            OutputFormatter.render(res, format="json")
        else:
            OutputFormatter.render_success(res["message"])
        raise typer.Exit(code=SUCCESS)
    except typer.Exit:
        raise
    except Exception as e:
        OutputFormatter.render_error(str(e))
        raise typer.Exit(code=INTERNAL_ERROR)

@app.command("delete")
@timed_cli_command
def delete_cmd(
    name: str = typer.Argument(..., help="Profile name to delete"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format")
):
    try:
        dest_path = PROFILES_DIR / f"{name}.yaml"
        if not dest_path.exists():
            OutputFormatter.render_error(f"Profile {name} not found.")
            raise typer.Exit(code=NOT_FOUND)
            
        dest_path.unlink()
        
        res = {"status": "success", "message": f"Deleted profile {name}"}
        if json_out:
            OutputFormatter.render(res, format="json")
        else:
            OutputFormatter.render_success(res["message"])
        raise typer.Exit(code=SUCCESS)
    except typer.Exit:
        raise
    except Exception as e:
        OutputFormatter.render_error(str(e))
        raise typer.Exit(code=INTERNAL_ERROR)
