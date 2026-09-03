from __future__ import annotations

import argparse
import json
from pathlib import Path

from trafficlight.simulation.benchmark import run_benchmark
from trafficlight.simulation.failure_modes import run_failure_modes
from trafficlight.simulation.reporting import write_dissertation_report
from trafficlight.simulation.scenarios import SCENARIOS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate dissertation-ready experiment outputs.")
    parser.add_argument(
        "--scenario",
        action="append",
        dest="scenarios",
        default=[],
        help="Benchmark scenario to include. Repeat for multiple scenarios.",
    )
    parser.add_argument("--fault-scenario", default="ns-heavy")
    parser.add_argument("--seed", action="append", dest="seed_values", type=int, default=[])
    parser.add_argument("--seeds", dest="seed_count", type=int, default=5)
    parser.add_argument("--duration", type=float, default=300.0)
    parser.add_argument("--step", type=float, default=0.5)
    parser.add_argument("--output-dir", type=Path, default=Path("results/dissertation"))
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    scenarios = args.scenarios or tuple(SCENARIOS)
    seeds = tuple(args.seed_values or range(1, args.seed_count + 1))
    benchmark_rows = run_benchmark(
        scenarios=scenarios,
        seeds=seeds,
        duration_s=args.duration,
        step_s=args.step,
    )
    failure_rows = run_failure_modes(
        scenario=args.fault_scenario,
        seeds=seeds,
        duration_s=args.duration,
        step_s=args.step,
    )
    outputs = write_dissertation_report(
        benchmark_rows=benchmark_rows,
        failure_rows=failure_rows,
        output_dir=args.output_dir,
        duration_s=args.duration,
        step_s=args.step,
        seeds=seeds,
    )
    print(json.dumps({name: str(path) for name, path in outputs.items()}, indent=2))


if __name__ == "__main__":
    main()

