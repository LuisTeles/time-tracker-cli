# src/timetracker/cli/test_db.py
import click
from rich.console import Console
from rich.table import Table
from ..core.database import get_connection, init_db, insert_test_data

console = Console()

@click.command()
def test_db():
    """Show project-task relationships"""
    init_db()
    insert_test_data()
    
    with get_connection() as conn:
        # Projects with task counts
        console.print("[bold]Projects Summary[/bold]")
        projects = conn.execute("""
            SELECT p.id, p.name, COUNT(t.id) as task_count
            FROM projects p LEFT JOIN tasks t ON p.id = t.project_id
            GROUP BY p.id
        """).fetchall()
        
        for p in projects:
            console.print(f"{p['name']} ([cyan]{p['id']}[/cyan]): {p['task_count']} tasks")

        # Recent tasks
        console.print("\n[bold]Recent Tasks[/bold]")
        tasks = conn.execute("""
            SELECT t.id, p.name as project, t.name, t.status, t.date
            FROM tasks t JOIN projects p ON t.project_id = p.id
            ORDER BY t.date DESC LIMIT 5
        """).fetchall()
        
        for t in tasks:
            console.print(
                f"{t['date']}: [yellow]{t['project']}[/yellow] - {t['name']} "
                f"({t['status'].replace('_', ' ')})"
            )