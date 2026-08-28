from __future__ import annotations

import argparse
import json
from pathlib import Path

from trafficlight.simulation.benchmark import (
    benchmark_rows_to_dicts,
    run_benchmark,
    write_benchmark_csv,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare fixed-time and adaptive controllers.")
    parser.add_argument(
        "--scenario",
        action="append",
        dest="scenarios",
        default=[],
        help="Scenario to run. Repeat for multiple scenarios. Defaults to all core scenarios.",
    )
    parser.add_argument(
        "--seed",
        action="append",
        dest="seeds",
        type=int,
        default=[],
        help="Random seed to run. Repeat for multiple seeds.",
    )
    parser.add_argument("--duration", type=float, default=300.0)
    parser.add_argument("--step", type=float, default=0.5)
    parser.add_argument("--csv", type=Path, default=Path("results/benchmark.csv"))
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    rows = run_benchmark(
        scenarios=args.scenarios or ("balanced", "ns-heavy", "ew-heavy"),
        seeds=args.seeds or (42,),
        duration_s=args.duration,
        step_s=args.step,
    )
    csv_path = write_benchmark_csv(rows, args.csv)
    print(json.dumps({"csv": str(csv_path), "rows": benchmark_rows_to_dicts(rows)}, indent=2))


if __name__ == "__main__":
    main()

