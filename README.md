# Smart Traffic-Light Controller

Simulation-first adaptive traffic-light controller for a final-year Raspberry Pi project.

The important design decision is that the controller does not know about GPIO. It talks to
small interfaces for signals, detectors, and clocks. Simulation and Raspberry Pi hardware can
therefore use the same control logic.

## Current MVP

- Safe four-way phase state machine for North/South and East/West movements.
- Fixed-time controller baseline.
- Adaptive controller that changes green duration from demand while enforcing min/max green.
- Simulated signal driver and traffic queue model.
- SQLite run, event, detector, and queue-metric logging.
- Browser dashboard with live intersection state, queue metrics, and visible vehicles.
- Fixed-vs-adaptive benchmark runner with CSV export.
- CLI simulation summary.
- pytest safety and scenario tests.

## Setup

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
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

Run the API:

```powershell
python -m pip install -e ".[api]"
uvicorn trafficlight.api.app:app --reload
```

Open the dashboard at `http://127.0.0.1:8000/`.

Run a fixed-vs-adaptive benchmark and export CSV:

```powershell
python scripts/benchmark.py --duration 300 --step 0.5 --csv results/benchmark.csv
```

Useful endpoints:

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
  interfaces/    small protocols for hardware-independent code
  simulation/    virtual signals and traffic queue simulator
  hardware/      Raspberry Pi adapters will live here
  api/           FastAPI dashboard/API will live here
  storage/       SQLite logging will live here
```

## Next Milestones

1. Add GPIO Zero adapter with mock-pin tests.
2. Add Raspberry Pi deployment service.
