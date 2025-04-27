import click
from rich.console import Console
from ..core.database import get_connection
from datetime import datetime

console = Console()

@click.command()
@click.option('--project', required=True, help="Project ID")
@click.option('--name', required=True, help="Task name")
@click.option('--duration', type=int, help="Duration in minutes")
def add_task(project, name, duration):
    """Add a real task from user input"""
    task_id = f"task_{project[:2]}_{datetime.now().strftime('%H%M')}"
    
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO tasks (id, project_id, name, date, status, duration_mins)
            VALUES (?, ?, ?, ?, 'todo', ?)
            """,
            (task_id, project, name, datetime.now().date().isoformat(), duration)
        )
        conn.commit()
    
    console.print(f"[green]✓ Added task:[/green] {name} (ID: {task_id})")

# Register in main.py:
# from .tasks import add_task
# cli.add_command(add_task)