from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict

from trafficlight.domain.models import ControllerStatus, DemandSnapshot


class SQLiteSimulationLogger:
    def __init__(self, connection: sqlite3.Connection, *, sample_interval_s: float = 1.0) -> None:
        if sample_interval_s <= 0:
            raise ValueError("sample_interval_s must be positive")
        self.connection = connection
        self.sample_interval_s = sample_interval_s
        self._last_sample_at: float | None = None
        self._last_phase: str | None = None

    def start_run(self, config: dict) -> int:
        cursor = self.connection.execute(
            """
            INSERT INTO runs (
                scenario,
                controller,
                duration_s,
                step_s,
                seed,
                config_json,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                config["scenario"],
                config["controller"],
                config["duration_s"],
                config["step_s"],
                config["seed"],
                json.dumps(config, sort_keys=True),
                "running",
            ),
        )
        self.connection.commit()
        self._last_sample_at = None
        self._last_phase = None
        return int(cursor.lastrowid)

    def record_step(
        self,
        *,
        run_id: int,
        timestamp: float,
        demand: DemandSnapshot,
        status: ControllerStatus,
        queues: dict[str, int],
        completed_vehicles: int,
        mean_wait_s: float | None,
    ) -> None:
        if self._last_phase != status.phase.value:
            self.connection.execute(
                """
                INSERT INTO signal_events (run_id, timestamp, from_phase, to_phase, reason)
                VALUES (?, ?, ?, ?, ?)
                """,
                (run_id, timestamp, self._last_phase, status.phase.value, status.reason),
            )
            self._last_phase = status.phase.value

        should_sample = (
            self._last_sample_at is None
            or timestamp - self._last_sample_at >= self.sample_interval_s
        )
        if not should_sample:
            return

        self.connection.execute(
            """
            INSERT INTO detector_samples (
                run_id,
                timestamp,
                north_demand,
                east_demand,
                south_demand,
                west_demand
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (run_id, timestamp, demand.north, demand.east, demand.south, demand.west),
        )
        self.connection.execute(
            """
            INSERT INTO traffic_metrics (
                run_id,
                timestamp,
                north_queue,
                east_queue,
                south_queue,
                west_queue,
                completed_vehicles,
                mean_wait_s
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                timestamp,
                queues["north"],
                queues["east"],
                queues["south"],
                queues["west"],
                completed_vehicles,
                mean_wait_s,
            ),
        )
        self.connection.commit()
        self._last_sample_at = timestamp

    def finish_run(self, run_id: int, summary: dict) -> None:
        self.connection.execute(
            """
            UPDATE runs
            SET finished_at = CURRENT_TIMESTAMP,
                status = ?,
                summary_json = ?
            WHERE id = ?
            """,
            ("completed", json.dumps(summary, sort_keys=True), run_id),
        )
        self.connection.commit()


def row_counts(connection: sqlite3.Connection, run_id: int) -> dict[str, int]:
    counts = {}
    for table in ("detector_samples", "signal_events", "traffic_metrics"):
        row = connection.execute(
            f"SELECT COUNT(*) AS count FROM {table} WHERE run_id = ?",
            (run_id,),
        ).fetchone()
        counts[table] = int(row["count"])
    return counts


def list_runs(connection: sqlite3.Connection, *, limit: int = 20) -> list[dict]:
    rows = connection.execute(
        """
        SELECT
            id,
            started_at,
            finished_at,
            scenario,
            controller,
            duration_s,
            step_s,
            seed,
            status,
            summary_json
        FROM runs
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [dict(row) for row in rows]


def get_run(connection: sqlite3.Connection, run_id: int) -> dict | None:
    row = connection.execute(
        """
        SELECT
            id,
            started_at,
            finished_at,
            scenario,
            controller,
            duration_s,
            step_s,
            seed,
            status,
            summary_json
        FROM runs
        WHERE id = ?
        """,
        (run_id,),
    ).fetchone()
    return dict(row) if row is not None else None


def list_metrics(connection: sqlite3.Connection, run_id: int, *, limit: int = 500) -> list[dict]:
    rows = connection.execute(
        """
        SELECT
            timestamp,
            north_queue,
            east_queue,
            south_queue,
            west_queue,
            completed_vehicles,
            mean_wait_s
        FROM traffic_metrics
        WHERE run_id = ?
        ORDER BY timestamp ASC
        LIMIT ?
        """,
        (run_id, limit),
    ).fetchall()
    return [dict(row) for row in rows]


def summary_to_dict(summary) -> dict:
    return asdict(summary)
