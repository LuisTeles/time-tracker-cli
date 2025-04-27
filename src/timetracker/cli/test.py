import click
from rich.console import Console
from rich.table import Table
from ..core.database import init_db

console = Console()

@click.command()
def test():
    """Test screen to verify all components"""
    # 1. Test database
    init_db()
    console.print("[green]✓ Database initialized[/green]")

    # 2. Test Rich output
    table = Table(title="Test Components")
    table.add_column("Component", style="cyan")
    table.add_column("Status", justify="right")

    table.add_row("Click CLI", "[green]Working[/green]")
    table.add_row("Rich Display", "[green]Working[/green]")
    table.add_row("SQLite DB", "[green]Connected[/green]")

    console.print(table)
    console.print("\n[bold yellow]All systems go![/bold yellow]")
