from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from trafficlight.simulation.faults import fault_profiles
from trafficlight.simulation.runner import run_simulation


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run adaptive-control detector fault scenarios.")
    parser.add_argument("--scenario", default="ns-heavy")
    parser.add_argument("--duration", type=float, default=300.0)
    parser.add_argument("--step", type=float, default=0.5)
    parser.add_argument("--seed", action="append", dest="seed_values", type=int, default=[])
    parser.add_argument("--seeds", dest="seed_count", type=int, default=1)
    parser.add_argument("--csv", type=Path, default=Path("results/failure_modes.csv"))
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    seeds = args.seed_values or tuple(range(1, args.seed_count + 1))
    rows = []
    for seed in seeds:
        for fault_name, faults in fault_profiles(args.duration).items():
            summary = run_simulation(
                controller_name="adaptive",
                scenario_name=args.scenario,
                duration_s=args.duration,
                step_s=args.step,
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
    write_csv(rows, args.csv)
    print(json.dumps({"csv": str(args.csv), "rows": rows}, indent=2))


def write_csv(rows: list[dict], path: Path) -> None:
    if path.parent != Path("."):
        path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
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
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()

