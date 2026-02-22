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
        create_db_and_tables()
        
    try:
            drop_all()
            create_db_and_tables()
    except:
            pass  
    csv_path = "pokemon.csv"
        
    try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                
                pokemon_count = 0
                error_count = 0
                
                for row in csv_reader:
                    try:
                        pokemon = Pokemon(
                            name=row['name'],
                            attack=int(float(row['attack'])) if row['attack'] else 0,
                            defense=int(float(row['defense'])) if row['defense'] else 0,
                            hp=int(float(row['hp'])) if row['hp'] else 0,
                            height=float(row['height_m']) if row['height_m'] else 0.0,
                            weight=float(row['weight_kg']) if row['weight_kg'] else 0.0,
                            sp_attack=int(float(row['sp_attack'])) if row['sp_attack'] else 0,
                            sp_defense=int(float(row['sp_defense'])) if row['sp_defense'] else 0,
                            speed=int(float(row['speed'])) if row['speed'] else 0,
                            type1=row['type1'].strip() if row['type1'] else '',
                            type2=row['type2'].strip() if row['type2'] and row['type2'].strip() else None
                        )
                        
                        db.add(pokemon)
                        pokemon_count += 1
                        
                        if pokemon_count % 100 == 0:
                            db.commit()
                            typer.echo(f"Committed {pokemon_count} Pokemon...")
                            
                    except Exception as e:
                        error_count += 1
                        typer.echo(f"Error processing row {pokemon_count + error_count}: {row.get('name', 'Unknown')}")
                        typer.echo(f"Error details: {str(e)}")
                        continue
                db.commit()
                
                typer.echo(f"\nImport completed!")
                typer.echo(f"Successfully imported: {pokemon_count} Pokemon")
                typer.echo(f"Errors encountered: {error_count}")
                
    except FileNotFoundError:
            typer.echo(f"Error: Could not find {csv_path} file")
            raise
    except Exception as e:
            typer.echo(f"Error reading CSV file: {str(e)}")
            raise

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