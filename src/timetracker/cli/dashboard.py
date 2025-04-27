# src/timetracker/cli/dashboard.py
from textual.app import App, ComposeResult
from textual.widgets import (Header, Footer, DataTable, Static, 
                           Button, Input, Switch, Label)
from textual.containers import Horizontal, Container
from textual.screen import ModalScreen
from datetime import datetime
from ..core.database import get_connection

class AddTaskDialog(ModalScreen):
    """Dialog for adding new tasks"""
    
    def compose(self) -> ComposeResult:
        yield Label("Add New Task")
        yield Input(placeholder="Task name", id="task-name")
        yield Input(placeholder="Project ID", id="project-id")
        yield Horizontal(
            Button("Cancel", id="cancel-btn"),
            Button("Confirm", id="confirm-btn"),
        )

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "confirm-btn":
            self.dismiss({
                "name": self.query_one("#task-name", Input).value,
                "project": self.query_one("#project-id", Input).value
            })
        else:
            self.dismiss(None)

class TimeTrackerDashboard(App):
    CSS = """
    DataTable {
        height: 65%;
    }
    .stats {
        height: 15%;
        border: solid $accent;
        padding: 1;
    }
    .controls {
        height: 20%;
        layout: horizontal;
    }
    Button {
        width: 16;
    }
    #filter-input {
        width: 30%;
    }
    AddTaskDialog {
        width: 60;
        height: auto;
    }
    .dialog-title {
        text-align: center;
        width: 100%;
        margin-bottom: 1;
    }

    .dialog-buttons {
    width: 100%;
    height: auto;
    margin-top: 1;
    align: right middle;
    }
    
    #task-name, #project-id {
        width: 100%;
        margin-bottom: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable()
        yield Container(
            Horizontal(
                Button("Mark Complete", id="mark-complete"),
                Button("Add Task", id="add-btn"),
                Input(placeholder="Filter tasks...", id="filter-input"),
                Switch("Today Only", id="today-switch"),
            ),
            classes="controls"
        )
        yield Container(Static(id="stats"), classes="stats")
        yield Footer()

    def on_mount(self):
        self.set_up_table()
        self.update_stats()

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "mark-complete":
            self.mark_task_complete()
        elif event.button.id == "add-btn":
            await self.add_new_task()

    def on_input_changed(self, event: Input.Changed):
        self.filter_tasks(event.value)

    def on_switch_changed(self, event: Switch.Changed):
        self.today_only = event.value
        self.refresh_table()

    def set_up_table(self):
        table = self.query_one(DataTable)
        table.add_columns("ID", "Task", "Project", "Status", "Due")
        
        with get_connection() as conn:
            tasks = conn.execute("""
                SELECT t.id, t.name, p.name as project, t.status, t.date 
                FROM tasks t JOIN projects p ON t.project_id = p.id
                ORDER BY t.date
            """).fetchall()
            
            for task in tasks:
                status = {
                    'todo': '[yellow]⬤[/yellow] Todo',
                    'in_progress': '[blue]⬤[/blue] In Progress',
                    'done': '[green]⬤[/green] Done'
                }.get(task['status'], task['status'])
                
                table.add_row(
                    task['id'],
                    task['name'],
                    task['project'],
                    status,
                    task['date']
                )

    def update_stats(self):
        with get_connection() as conn:
            stats = conn.execute("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN status='done' THEN 1 ELSE 0 END) as done
                FROM tasks
            """).fetchone()
            
            self.query_one("#stats", Static).update(
                f"[b]Tasks:[/b] {stats['done']}/{stats['total']} completed\n"
                f"[b]Focus Score:[/b] 8/10 today"
            )

    def mark_task_complete(self):
        table = self.query_one(DataTable)
        if table.cursor_row is not None:
            task_id = table.get_row_at(table.cursor_row)[0]
            with get_connection() as conn:
                conn.execute(
                    "UPDATE tasks SET status='done' WHERE id=?",
                    (task_id,)
                )
                conn.commit()
            self.refresh_table()
            self.notify("Task marked complete!", severity="success")

    def filter_tasks(self, search_term: str):
        self.search_term = search_term.lower()
        self.refresh_table()

    def refresh_table(self):
        table = self.query_one(DataTable)
        table.clear()
        
        query = """
            SELECT t.id, t.name, p.name as project, t.status, t.date 
            FROM tasks t JOIN projects p ON t.project_id = p.id
            WHERE 1=1
        """
        params = []
        
        if hasattr(self, 'today_only') and self.today_only:
            query += " AND t.date = ?"
            params.append(datetime.now().date().isoformat())
            
        if hasattr(self, 'search_term') and self.search_term:
            query += " AND (t.name LIKE ? OR p.name LIKE ?)"
            params.extend([f"%{self.search_term}%"] * 2)
            
        query += " ORDER BY t.date"
        
        with get_connection() as conn:
            tasks = conn.execute(query, params).fetchall()
            for task in tasks:
                status = {
                    'todo': '[yellow]⬤[/yellow] Todo',
                    'in_progress': '[blue]⬤[/blue] In Progress', 
                    'done': '[green]⬤[/green] Done'
                }.get(task['status'], task['status'])
                
                table.add_row(
                    task['id'],
                    task['name'],
                    task['project'],
                    status,
                    task['date']
                )

    async def add_new_task(self):
        """Show dialog and handle new task creation"""
        dialog = AddTaskDialog()
        result = await self.push_screen(dialog)   # <-- fix here!

        if result:
            with get_connection() as conn:
                conn.execute(
                    """INSERT INTO tasks 
                    (id, name, project_id, date, status)
                    VALUES (?, ?, ?, ?, 'todo')""",
                    (
                        f"task_{datetime.now().timestamp()}",  # Unique ID
                        result["name"],
                        result["project"],
                        datetime.now().date().isoformat()
                    )
                )
                conn.commit()
            self.refresh_table()
            self.notify("Task added successfully!")


if __name__ == "__main__":
    app = TimeTrackerDashboard()
    app.run()