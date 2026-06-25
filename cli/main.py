import typer
from cli.commands import app as commands_app

app = typer.Typer(help="BugHunter CLI")
app.add_typer(commands_app, name="")

if __name__ == "__main__":
    app()
