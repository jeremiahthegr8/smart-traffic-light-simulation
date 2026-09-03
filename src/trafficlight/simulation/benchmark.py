from __future__ import annotations

import csv
import math
import statistics
from dataclasses import dataclass
from pathlib import Path

from trafficlight.simulation.runner import run_simulation
from trafficlight.simulation.scenarios import SCENARIOS


CONTROLLERS: tuple[str, str] = ("fixed", "adaptive")


@dataclass(frozen=True)
class BenchmarkRow:
    scenario: str
    seed: int
    controller: str
    arrivals: int
    completed: int
    throughput_veh_per_min: float
    mean_wait_s: float
    max_queue: int
    conflicting_green_violations: int
    completed_delta_vs_fixed: int | None = None
    mean_wait_improvement_pct: float | None = None
    max_queue_improvement_pct: float | None = None


def run_benchmark(
    *,
    scenarios: list[str] | tuple[str, ...] = tuple(SCENARIOS),
    seeds: list[int] | tuple[int, ...] = (42,),
    duration_s: float = 300.0,
    step_s: float = 0.5,
) -> list[BenchmarkRow]:
    if duration_s <= 0:
        raise ValueError("duration_s must be positive")
    if step_s <= 0:
        raise ValueError("step_s must be positive")

    rows: list[BenchmarkRow] = []
    for scenario in scenarios:
        if scenario not in SCENARIOS:
            raise ValueError(f"unknown scenario: {scenario}")
        for seed in seeds:
            fixed = _run_one("fixed", scenario, seed, duration_s, step_s)
            adaptive = _run_one("adaptive", scenario, seed, duration_s, step_s)
            rows.append(fixed)
            rows.append(_with_comparison(adaptive, fixed))
    return rows


def write_benchmark_csv(rows: list[BenchmarkRow], path: str | Path) -> Path:
    output_path = Path(path)
    if output_path.parent != Path("."):
        output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = list(BenchmarkRow.__dataclass_fields__)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)
    return output_path


def benchmark_rows_to_dicts(rows: list[BenchmarkRow]) -> list[dict]:
    return [row.__dict__ for row in rows]


def aggregate_benchmark(rows: list[BenchmarkRow]) -> list[dict]:
    grouped: dict[tuple[str, str], list[BenchmarkRow]] = {}
    for row in rows:
        grouped.setdefault((row.scenario, row.controller), []).append(row)

    aggregates = []
    for (scenario, controller), group in sorted(grouped.items()):
        completed = _stats(row.completed for row in group)
        mean_wait = _stats(row.mean_wait_s for row in group)
        max_queue = _stats(row.max_queue for row in group)
        completed_delta = _stats_or_none(row.completed_delta_vs_fixed for row in group)
        wait_improvement = _stats_or_none(row.mean_wait_improvement_pct for row in group)
        queue_improvement = _stats_or_none(row.max_queue_improvement_pct for row in group)
        aggregates.append(
            {
                "scenario": scenario,
                "controller": controller,
                "runs": len(group),
                "mean_completed": completed["mean"],
                "std_completed": completed["std"],
                "ci95_completed": completed["ci95"],
                "mean_wait_s": mean_wait["mean"],
                "std_wait_s": mean_wait["std"],
                "ci95_wait_s": mean_wait["ci95"],
                "mean_max_queue": max_queue["mean"],
                "std_max_queue": max_queue["std"],
                "ci95_max_queue": max_queue["ci95"],
                "total_conflicting_green_violations": sum(
                    row.conflicting_green_violations for row in group
                ),
                "mean_completed_delta_vs_fixed": completed_delta["mean"],
                "std_completed_delta_vs_fixed": completed_delta["std"],
                "ci95_completed_delta_vs_fixed": completed_delta["ci95"],
                "mean_wait_improvement_pct": wait_improvement["mean"],
                "std_wait_improvement_pct": wait_improvement["std"],
                "ci95_wait_improvement_pct": wait_improvement["ci95"],
                "mean_max_queue_improvement_pct": queue_improvement["mean"],
                "std_max_queue_improvement_pct": queue_improvement["std"],
                "ci95_max_queue_improvement_pct": queue_improvement["ci95"],
            }
        )
    return aggregates


def _run_one(
    controller: str,
    scenario: str,
    seed: int,
    duration_s: float,
    step_s: float,
) -> BenchmarkRow:
    summary = run_simulation(
        controller_name=controller,
        scenario_name=scenario,
        duration_s=duration_s,
        step_s=step_s,
        seed=seed,
        db_path=None,
    )
    return BenchmarkRow(
        scenario=scenario,
        seed=seed,
        controller=controller,
        arrivals=summary["arrivals"],
        completed=summary["completed"],
        throughput_veh_per_min=summary["throughput_veh_per_min"],
        mean_wait_s=summary["mean_wait_s"],
        max_queue=summary["max_queue"],
        conflicting_green_violations=summary["conflicting_green_violations"],
    )


def _with_comparison(adaptive: BenchmarkRow, fixed: BenchmarkRow) -> BenchmarkRow:
    return BenchmarkRow(
        scenario=adaptive.scenario,
        seed=adaptive.seed,
        controller=adaptive.controller,
        arrivals=adaptive.arrivals,
        completed=adaptive.completed,
        throughput_veh_per_min=adaptive.throughput_veh_per_min,
        mean_wait_s=adaptive.mean_wait_s,
        max_queue=adaptive.max_queue,
        conflicting_green_violations=adaptive.conflicting_green_violations,
        completed_delta_vs_fixed=adaptive.completed - fixed.completed,
        mean_wait_improvement_pct=_improvement_pct(fixed.mean_wait_s, adaptive.mean_wait_s),
        max_queue_improvement_pct=_improvement_pct(float(fixed.max_queue), float(adaptive.max_queue)),
    )


def _improvement_pct(baseline: float, candidate: float) -> float | None:
    if baseline <= 0:
        return None
    return ((baseline - candidate) / baseline) * 100.0


def _mean(values) -> float:
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def _stats(values) -> dict[str, float]:
    values = [float(value) for value in values]
    if not values:
        return {"mean": 0.0, "std": 0.0, "ci95": 0.0}

    mean = _mean(values)
    if len(values) < 2:
        return {"mean": mean, "std": 0.0, "ci95": 0.0}

    std = statistics.stdev(values)
    ci95 = 1.96 * std / math.sqrt(len(values))
    return {"mean": mean, "std": std, "ci95": ci95}


def _stats_or_none(values) -> dict[str, float | None]:
    values = [value for value in values if value is not None]
    if not values:
        return {"mean": None, "std": None, "ci95": None}
    return _stats(values)
