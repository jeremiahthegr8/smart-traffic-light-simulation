# Smart Traffic-Light Simulation

Adaptive traffic-light control project implemented as a full software simulation.

This branch intentionally removes Raspberry Pi and GPIO hardware from the project scope. The
focus is now the controller algorithm, live simulation dashboard, repeatable experiments, data
logging, and fixed-vs-adaptive evaluation.

## Current Scope

- Safe four-way phase state machine for North/South and East/West movements.
- Fixed-time controller baseline.
- Adaptive controller that changes green duration from demand while enforcing min/max green.
- Time-varying traffic scenarios with repeatable random seeds.
- SQLite run, event, detector, and queue-metric logging.
- Browser dashboard with live intersection state, queue metrics, and visible vehicles.
- Fixed-vs-adaptive benchmark runner with CSV export and aggregate statistics.
- Multi-seed spread measures including standard deviation and 95% confidence intervals.
- Detector fault simulation for stuck-high and stuck-low demand readings.
- Dashboard fault-profile controls showing queue counts versus detector readings.
- Dashboard benchmark charts for aggregate fixed-vs-adaptive comparison.
- FastAPI API and WebSocket stream.
- pytest safety, scenario, storage, benchmark, and API tests.

## Setup

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,api]"
pytest
```

Run a short simulation:

```powershell
python -m trafficlight.main --controller adaptive --duration 300 --scenario ns-heavy
python -m trafficlight.main --controller fixed --duration 300 --scenario ns-heavy
```

By default, runs are logged to `trafficlight.db`. Disable logging when you only want
terminal output:

```powershell
python -m trafficlight.main --controller adaptive --duration 300 --scenario ns-heavy --no-db
```

Run the dashboard:

```powershell
uvicorn trafficlight.api.app:app --reload
```

Open `http://127.0.0.1:8000/`.

Run a fixed-vs-adaptive benchmark and export CSV:

```powershell
python scripts/benchmark.py --duration 300 --step 0.5 --seeds 5 --csv results/benchmark.csv --summary-csv results/benchmark_summary.csv --charts results/charts
```

The benchmark script writes:

- row-level CSV results
- aggregate summary CSV with means, standard deviation, and 95% confidence intervals
- SVG charts for mean wait, max queue, and completed vehicles

Run detector fault simulations:

```powershell
python scripts/failure_modes.py --scenario ns-heavy --duration 300 --step 0.5 --seeds 5 --csv results/failure_modes.csv
```

Generate the full dissertation results package:

```powershell
python scripts/dissertation_results.py --duration 300 --step 0.5 --seeds 5 --output-dir results/dissertation
```

This writes CSV files, SVG charts, and `results_summary.md`.

## Scenarios

- `balanced`: similar demand on all four approaches.
- `ns-heavy`: North/South demand is much higher than East/West demand.
- `ew-heavy`: East/West demand is much higher than North/South demand.
- `ns-burst`: short North/South demand surge during moderate traffic.
- `alternating-peak`: demand shifts from North/South to East/West during the run.

## API

- `GET /health`
- `GET /api/scenarios`
- `POST /api/simulations`
- `POST /api/benchmarks`
- `GET /api/runs`
- `GET /api/runs/{run_id}/metrics`
- `WS /ws/simulation`

## Project Shape

```text
src/trafficlight/
  domain/        core models, safety checks, fixed/adaptive controllers
  interfaces/    small protocols for simulation services
  simulation/    traffic scenarios, queue engine, benchmark runner
  api/           FastAPI dashboard/API
  storage/       SQLite logging
```

## Next Milestones

1. Prepare a short demonstration script using the saved dashboard screenshots and benchmark outputs.
2. Polish the final report draft into your institution's required formatting.
