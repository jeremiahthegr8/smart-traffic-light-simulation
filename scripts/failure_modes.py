from __future__ import annotations

import argparse
import json
from pathlib import Path

from trafficlight.simulation.failure_modes import run_failure_modes, write_failure_modes_csv


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
    rows = run_failure_modes(
        scenario=args.scenario,
        seeds=tuple(seeds),
        duration_s=args.duration,
        step_s=args.step,
    )
    write_failure_modes_csv(rows, args.csv)
    print(json.dumps({"csv": str(args.csv), "rows": rows}, indent=2))


if __name__ == "__main__":
    main()
