from __future__ import annotations

import argparse
import json
from pathlib import Path

from trafficlight.simulation.scenarios import SCENARIOS
from trafficlight.simulation.runner import run_simulation


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a smart traffic-light simulation.")
    parser.add_argument("--controller", choices=["fixed", "adaptive"], default="adaptive")
    parser.add_argument("--scenario", choices=sorted(SCENARIOS), default="ns-heavy")
    parser.add_argument("--duration", type=float, default=300.0)
    parser.add_argument("--step", type=float, default=0.5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--db", type=Path, default=Path("trafficlight.db"))
    parser.add_argument("--no-db", action="store_true")
    parser.add_argument("--sample-interval", type=float, default=1.0)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    summary = run_simulation(
        controller_name=args.controller,
        scenario_name=args.scenario,
        duration_s=args.duration,
        step_s=args.step,
        seed=args.seed,
        db_path=None if args.no_db else args.db,
        sample_interval_s=args.sample_interval,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
