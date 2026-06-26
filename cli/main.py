import typer
import sys
from cli.commands import app as commands_app
from version import __version__

def version_callback(value: bool):
    if value:
        from rich.console import Console
        console = Console()
        console.print(f"BugHunter v{__version__}")
        raise typer.Exit()

app = typer.Typer(help="BugHunter CLI")
app.callback()(
    lambda version: version_callback(version)
    if version else None
)

@app.callback()
def main_callback(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show the application version and exit.",
    )
):
    """BugHunter CLI Application."""
    pass

app.add_typer(commands_app, name="")

def main():
    app()

if __name__ == "__main__":
    main()
