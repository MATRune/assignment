import typer
import csv
from sqlmodel import select
from app.database import create_db_and_tables, get_cli_session, drop_all
from app.models import *
from app.auth import encrypt_password
import subprocess

cli = typer.Typer()

@cli.command()
def initialize():
    with get_cli_session() as db:
        pass

@cli.command()
def test():
    try:
        subprocess.run(["npm", "install"], check=True)
    except subprocess.CalledProcessError:
        typer.secho("Installing test package failed. Install Node/npm on your PC to continue", fg=typer.colors.RED)
        raise typer.Exit(code=1)
        
    try:
        subprocess.run(["npm", "test"], check=True)
    except subprocess.CalledProcessError:
        typer.secho("Tests failed!", fg=typer.colors.RED)
        raise typer.Exit(code=1)

if __name__ == "__main__":
    cli()