import click
from .test import test  # Import the test command
from .test_db import test_db  # Import the test_db command
from .tasks import add_task  # Import the add_task command
from .dashboard import TimeTrackerDashboard

@click.group()
def cli():
    """Time Tracker CLI"""
    pass

cli.add_command(test)  # Register the test command

if __name__ == "__main__":
    cli()

cli.add_command(test_db)

if __name__ == "__main__":
    cli()

cli.add_command(add_task)  # Register the add_task command

@cli.command()
def dashboard():
    """Launch interactive dashboard"""
    TimeTrackerDashboard().run()

if __name__ == "__main__":
    cli()