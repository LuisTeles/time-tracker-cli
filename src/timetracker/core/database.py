# src/timetracker/core/database.py
import sqlite3
import json
from pathlib import Path
from typing import Optional
from datetime import datetime

DB_PATH = Path.home() / ".timetracker.db"

def get_connection():
    """Return a database connection with proper settings"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    return conn

def init_db():
    """Initialize database with all tables"""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Projects table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            start_date TEXT NOT NULL,
            target_date TEXT,
            status TEXT CHECK(status IN ('active', 'paused', 'completed')),
            priority INTEGER CHECK(priority BETWEEN 1 AND 5),
            tags TEXT  -- JSON array stored as text
        )
        """)
        
        # Tasks table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            project_id TEXT REFERENCES projects(id),
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            status TEXT CHECK(status IN ('todo', 'in_progress', 'done')),
            duration_mins INTEGER,
            energy_level INTEGER CHECK(energy_level BETWEEN 1 AND 10),
            notes TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
        """)
        
        # Daily logs
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_logs (
            date TEXT PRIMARY KEY,
            total_tasks INTEGER,
            completed INTEGER,
            focus_score INTEGER CHECK(focus_score BETWEEN 1 AND 10),
            productivity TEXT CHECK(productivity IN ('high', 'medium', 'low'))
        )
        """)
        
        # Habits (optional)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            current_streak INTEGER DEFAULT 0,
            last_logged TEXT
        )
        """)
        
        conn.commit()

def insert_test_data():
    """Add realistic sample data"""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Sample Projects
        projects = [
            ('proj_german', 'Learn German', '2024-01-01', '2024-12-31', 'active', 2, json.dumps(["language", "daily"])),
            ('proj_python', 'Python CLI App', '2024-02-15', None, 'active', 1, json.dumps(["coding", "priority"])),
            ('proj_health', 'Gym Routine', '2024-03-01', '2024-06-30', 'paused', 3, json.dumps(["fitness"]))
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO projects VALUES (?, ?, ?, ?, ?, ?, ?)",
            projects
        )

        # Sample Tasks (linked to projects)
        tasks = [
            ('task_ge_001', 'proj_german', 'Complete Lesson 1', '2024-03-20', 'done', 45, 7, 'Used Anki flashcards'),
            ('task_ge_002', 'proj_german', 'Watch German film', '2024-03-21', 'todo', None, None, 'Plan for weekend'),
            ('task_py_001', 'proj_python', 'Setup database', '2024-03-20', 'done', 120, 8, 'SQLite works!'),
            ('task_py_002', 'proj_python', 'Implement CLI', '2024-03-21', 'in_progress', 30, 5, 'Using Click')
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO tasks VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            tasks
        )

        # Daily Logs
        daily_logs = [
            ('2024-03-20', 5, 3, 8, 'high'),
            ('2024-03-21', 4, 1, 5, 'medium')
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO daily_logs VALUES (?, ?, ?, ?, ?)",
            daily_logs
        )
        
        conn.commit()