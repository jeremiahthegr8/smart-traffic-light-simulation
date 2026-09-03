from __future__ import annotations

import csv
from pathlib import Path

from trafficlight.simulation.faults import fault_profiles
from trafficlight.simulation.runner import run_simulation


FAILURE_MODE_FIELDS = [
    "fault",
    "scenario",
    "seed",
    "arrivals",
    "completed",
    "throughput_veh_per_min",
    "mean_wait_s",
    "max_queue",
    "conflicting_green_violations",
]


def run_failure_modes(
    *,
    scenario: str = "ns-heavy",
    seeds: tuple[int, ...] = (1,),
    duration_s: float = 300.0,
    step_s: float = 0.5,
) -> list[dict]:
    if duration_s <= 0:
        raise ValueError("duration_s must be positive")
    if step_s <= 0:
        raise ValueError("step_s must be positive")

    rows = []
    for seed in seeds:
        for fault_name, faults in fault_profiles(duration_s).items():
            summary = run_simulation(
                controller_name="adaptive",
                scenario_name=scenario,
                duration_s=duration_s,
                step_s=step_s,
                seed=seed,
                db_path=None,
                sensor_faults=faults,
            )
            rows.append(
                {
                    "fault": fault_name,
                    "scenario": summary["scenario"],
                    "seed": seed,
                    "arrivals": summary["arrivals"],
                    "completed": summary["completed"],
                    "throughput_veh_per_min": summary["throughput_veh_per_min"],
                    "mean_wait_s": summary["mean_wait_s"],
                    "max_queue": summary["max_queue"],
                    "conflicting_green_violations": summary["conflicting_green_violations"],
                }
            )
    return rows


def write_failure_modes_csv(rows: list[dict], path: str | Path) -> Path:
    output_path = Path(path)
    if output_path.parent != Path("."):
        output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FAILURE_MODE_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def aggregate_failure_modes(rows: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = {}
    for row in rows:
        grouped.setdefault(row["fault"], []).append(row)

    aggregates = []
    for fault, group in sorted(grouped.items()):
        aggregates.append(
            {
                "fault": fault,
                "runs": len(group),
                "mean_completed": _mean(float(row["completed"]) for row in group),
                "mean_wait_s": _mean(float(row["mean_wait_s"]) for row in group),
                "mean_max_queue": _mean(float(row["max_queue"]) for row in group),
                "total_conflicting_green_violations": sum(
                    int(row["conflicting_green_violations"]) for row in group
                ),
            }
        )
    return aggregates


def _mean(values) -> float:
    values = list(values)
    return sum(values) / len(values) if values else 0.0

