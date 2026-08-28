from __future__ import annotations

import sqlite3
from pathlib import Path


SCHEMA = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY,
    started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at TEXT,
    scenario TEXT NOT NULL,
    controller TEXT NOT NULL,
    duration_s REAL NOT NULL,
    step_s REAL NOT NULL,
    seed INTEGER NOT NULL,
    config_json TEXT NOT NULL,
    status TEXT NOT NULL,
    summary_json TEXT
);

CREATE TABLE IF NOT EXISTS detector_samples (
    id INTEGER PRIMARY KEY,
    run_id INTEGER NOT NULL,
    timestamp REAL NOT NULL,
    north_demand REAL NOT NULL,
    east_demand REAL NOT NULL,
    south_demand REAL NOT NULL,
    west_demand REAL NOT NULL,
    FOREIGN KEY(run_id) REFERENCES runs(id)
);

CREATE TABLE IF NOT EXISTS signal_events (
    id INTEGER PRIMARY KEY,
    run_id INTEGER NOT NULL,
    timestamp REAL NOT NULL,
    from_phase TEXT,
    to_phase TEXT NOT NULL,
    reason TEXT NOT NULL,
    FOREIGN KEY(run_id) REFERENCES runs(id)
);

CREATE TABLE IF NOT EXISTS traffic_metrics (
    id INTEGER PRIMARY KEY,
    run_id INTEGER NOT NULL,
    timestamp REAL NOT NULL,
    north_queue INTEGER NOT NULL,
    east_queue INTEGER NOT NULL,
    south_queue INTEGER NOT NULL,
    west_queue INTEGER NOT NULL,
    completed_vehicles INTEGER NOT NULL,
    mean_wait_s REAL,
    FOREIGN KEY(run_id) REFERENCES runs(id)
);
"""


def connect_database(path: str | Path) -> sqlite3.Connection:
    db_path = Path(path)
    if db_path.parent != Path("."):
        db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    initialize_database(connection)
    return connection


def initialize_database(connection: sqlite3.Connection) -> None:
    connection.executescript(SCHEMA)
    connection.commit()

