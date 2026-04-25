import sqlite3
import csv
import os
from pathlib import Path

DB_PATH = "flight_design.db"
MOCK_DIR = Path(__file__).parent / "mock_data"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY,
            name TEXT, client TEXT,
            budget_usd REAL, estimated_hours REAL,
            logged_hours REAL, status TEXT,
            deadline TEXT, hourly_rate REAL
        );
        CREATE TABLE IF NOT EXISTS time_entries (
            id INTEGER PRIMARY KEY,
            project_id INTEGER, date TEXT,
            hours REAL, description TEXT
        );
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY,
            invoice_number TEXT, client TEXT,
            project TEXT, amount_usd REAL,
            status TEXT, issue_date TEXT, due_date TEXT
        );
        CREATE TABLE IF NOT EXISTS contracts (
            id INTEGER PRIMARY KEY,
            client TEXT, project TEXT,
            status TEXT, sent_date TEXT, signed_date TEXT
        );
        CREATE TABLE IF NOT EXISTS calendar_events (
            id INTEGER PRIMARY KEY,
            title TEXT, client TEXT,
            date TEXT, start_time TEXT,
            duration_hours REAL, type TEXT
        );
        CREATE TABLE IF NOT EXISTS session (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            loaded INTEGER DEFAULT 0
        );
        INSERT OR IGNORE INTO session (id, loaded) VALUES (1, 0);
    """)
    conn.commit()
    conn.close()


def is_data_loaded() -> bool:
    conn = get_conn()
    row = conn.execute("SELECT loaded FROM session WHERE id=1").fetchone()
    conn.close()
    return bool(row and row["loaded"])


def clear_all_tables(conn):
    for table in ["projects", "time_entries", "invoices", "contracts", "calendar_events"]:
        conn.execute(f"DELETE FROM {table}")


def load_csv_to_db(conn, filename: str, table: str, columns: list[str]):
    path = MOCK_DIR / filename
    if not path.exists():
        return
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            vals = [row.get(col, "").strip() or None for col in columns]
            placeholders = ",".join(["?"] * len(columns))
            conn.execute(
                f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})",
                vals
            )


def seed_mock_data():
    conn = get_conn()
    clear_all_tables(conn)
    load_csv_to_db(conn, "projects.csv", "projects",
        ["id","name","client","budget_usd","estimated_hours","logged_hours","status","deadline","hourly_rate"])
    load_csv_to_db(conn, "time_entries.csv", "time_entries",
        ["id","project_id","date","hours","description"])
    load_csv_to_db(conn, "invoices.csv", "invoices",
        ["id","invoice_number","client","project","amount_usd","status","issue_date","due_date"])
    load_csv_to_db(conn, "contracts.csv", "contracts",
        ["id","client","project","status","sent_date","signed_date"])
    load_csv_to_db(conn, "calendar.csv", "calendar_events",
        ["id","title","client","date","start_time","duration_hours","type"])
    conn.execute("UPDATE session SET loaded=1 WHERE id=1")
    conn.commit()
    conn.close()


def seed_from_uploads(files: dict[str, list[dict]]):
    """files = {table_name: [row_dict, ...]}"""
    conn = get_conn()
    clear_all_tables(conn)
    table_columns = {
        "projects": ["id","name","client","budget_usd","estimated_hours","logged_hours","status","deadline","hourly_rate"],
        "time_entries": ["id","project_id","date","hours","description"],
        "invoices": ["id","invoice_number","client","project","amount_usd","status","issue_date","due_date"],
        "contracts": ["id","client","project","status","sent_date","signed_date"],
        "calendar_events": ["id","title","client","date","start_time","duration_hours","type"],
    }
    for table, rows in files.items():
        if table not in table_columns:
            continue
        cols = table_columns[table]
        for row in rows:
            vals = [row.get(col, "").strip() if row.get(col) else None for col in cols]
            placeholders = ",".join(["?"] * len(cols))
            conn.execute(
                f"INSERT OR IGNORE INTO {table} ({','.join(cols)}) VALUES ({placeholders})",
                vals
            )
    conn.execute("UPDATE session SET loaded=1 WHERE id=1")
    conn.commit()
    conn.close()


def fetch_all(table: str) -> list[dict]:
    conn = get_conn()
    rows = conn.execute(f"SELECT * FROM {table}").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_dashboard_stats() -> dict:
    conn = get_conn()
    active = conn.execute("SELECT COUNT(*) as n FROM projects WHERE status != 'Completed'").fetchone()["n"]
    overdue_amt = conn.execute(
        "SELECT COALESCE(SUM(amount_usd),0) as total FROM invoices WHERE status='Overdue'"
    ).fetchone()["total"]
    unsigned = conn.execute(
        "SELECT COUNT(*) as n FROM contracts WHERE status='Pending'"
    ).fetchone()["n"]
    overbudget = conn.execute(
        "SELECT COUNT(*) as n FROM projects WHERE logged_hours > estimated_hours AND status != 'Completed'"
    ).fetchone()["n"]
    conn.close()
    return {
        "active_projects": active,
        "overdue_amount": overdue_amt,
        "unsigned_contracts": unsigned,
        "overbudget_projects": overbudget,
    }
