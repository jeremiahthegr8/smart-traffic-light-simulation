# Methodology and Implementation Draft

This chapter describes the simulation-only implementation of the adaptive traffic-light project.
The system was designed to evaluate controller behaviour in repeatable software experiments rather
than on Raspberry Pi hardware.

## Development Methodology

The project uses an incremental engineering approach. The first step was to define a safe signal
phase model, then add fixed-time and adaptive timing policies, then build the traffic simulation
around those controllers. After the simulator was working, the project added persistence,
dashboard visualisation, benchmark scripts, detector-fault tests, and report-ready result export.

This order was chosen because the safety-critical state machine needed to be stable before adding
traffic demand, storage, or dashboard features. The same controller code is used by the command
line interface, the API, the dashboard stream, and the benchmark scripts. This avoids separate
logic paths for demonstration and evaluation.

The implementation is organised into four main layers:

| Layer | Purpose | Main files |
|---|---|---|
| Domain | Signal phases, controller timing, safety rules | `src/trafficlight/domain/` |
| Simulation | Queue model, traffic scenarios, faults, benchmarks | `src/trafficlight/simulation/` |
| Storage | SQLite run/event/metric logging | `src/trafficlight/storage/` |
| Interface | CLI, FastAPI endpoints, WebSocket stream, dashboard | `src/trafficlight/main.py`, `src/trafficlight/api/`, `src/trafficlight/dashboard/` |

## Signal Phase Model

The signal controller uses two movement groups: North/South and East/West. The phase sequence is:

1. All-red clearance before North/South green
2. North/South green
3. North/South amber
4. All-red clearance before East/West green
5. East/West green
6. East/West amber

The phase sequence is implemented by `BasePhaseController` in
`src/trafficlight/domain/controller.py`. Both the fixed-time and adaptive controllers inherit from
this base controller, so they share the same phase order and safety states. The timing policy can
change how long a green phase lasts, but it cannot skip amber or all-red clearance.

The signal state is represented by `SignalState` in `src/trafficlight/domain/models.py`. A state
maps each approach to red, amber, or green. The safety check in `src/trafficlight/domain/safety.py`
rejects any state where a North/South approach and an East/West approach are green at the same
time.

## Fixed-Time Controller

The fixed-time controller is the baseline for evaluation. It uses the same phase sequence as the
adaptive controller, but every green phase lasts for the configured fixed green time. In the
default timing configuration, this is 20 seconds. Amber and all-red timings are also fixed.

This controller is useful because it gives a simple comparison point. If adaptive timing improves
results, the improvement can be measured against a predictable baseline rather than against an
undefined manual timing strategy.

## Adaptive Controller

The adaptive controller extends the same base phase machine but calculates green duration from
detected queue demand. During a green phase, the controller compares demand on the active movement
group with demand on the opposing group. It then chooses a target green duration between the
configured minimum and maximum green times.

The default timing limits are:

- Minimum green: 8 seconds
- Fixed green baseline: 20 seconds
- Maximum green: 45 seconds
- Amber: 3 seconds
- All-red: 2 seconds

The adaptive policy increases green duration when the active movement group has a larger share of
total demand. It can also leave a green phase after the minimum green time if the active group has
no demand and the opposing group is waiting. The maximum green limit prevents a busy approach from
starving the opposing approach indefinitely.

The important design decision is that adaptive logic affects only green timing. It does not
directly set conflicting signal outputs. Every output still passes through the shared
`checked_state` safety function before being applied to the simulated signal driver.

## Traffic Simulation

The traffic simulator is implemented in `src/trafficlight/simulation/engine.py`. Each approach has
an `ApproachQueue` that tracks queued vehicles, total arrivals, total departures, and accumulated
waiting time.

At each simulation step:

1. The engine adds arrivals to each approach using the scenario's arrival rate.
2. It creates a true demand snapshot from the real queue lengths.
3. It applies any configured detector faults to produce the demand seen by the controller.
4. It advances the controller by one time step.
5. It checks for conflicting-green violations.
6. It discharges vehicles from approaches currently showing green.
7. It accumulates waiting time for vehicles still in queue.
8. It logs and publishes the step data if storage or dashboard callbacks are enabled.

Arrivals are repeatable because each run uses a fixed random seed. Paired benchmark runs use the
same scenario, duration, step size, and seed for the fixed-time and adaptive controllers. This
makes the fixed/adaptive comparison fair because both controllers receive the same traffic input
trace.

The default discharge model uses a 2.2-second headway per vehicle. This is a simplified
representation of saturation flow at a junction. It is suitable for comparing controller behaviour
inside the simulation, but it is not a calibrated real-world traffic-flow model.

## Scenarios

Traffic scenarios are defined in `src/trafficlight/simulation/scenarios.py`. Each scenario gives
arrival rates in vehicles per minute for the four approaches. Some scenarios also include demand
windows where rates change during the run.

The implemented scenarios are:

| Scenario | Purpose |
|---|---|
| `balanced` | Similar demand on all approaches |
| `ns-heavy` | North/South demand is higher than East/West demand |
| `ew-heavy` | East/West demand is higher than North/South demand |
| `ns-burst` | A temporary North/South demand surge occurs during otherwise moderate traffic |
| `alternating-peak` | Demand shifts from North/South to East/West halfway through the run |

These scenarios test both steady unequal demand and changing demand. That is important because the
adaptive controller is expected to help most when demand is uneven or changes over time.

## Detector Fault Simulation

Detector faults are implemented in `src/trafficlight/simulation/faults.py`. Faults alter the
demand snapshot seen by the adaptive controller while leaving the true queue state unchanged. This
lets the dashboard and experiments compare real queue lengths with faulty detector readings.

The implemented fault profiles are:

| Fault profile | Behaviour |
|---|---|
| `none` | No detector fault |
| `ns-stuck-high` | North/South detector demand is forced high |
| `ew-stuck-low` | East/West detector demand is forced to zero |
| `all-stuck-low-midrun` | All detector readings become zero halfway through the run |

Fault experiments are run by `src/trafficlight/simulation/failure_modes.py` and
`scripts/failure_modes.py`. These experiments measure performance degradation and verify that bad
demand readings do not cause conflicting-green signal states.

## Data Logging

SQLite logging is implemented in `src/trafficlight/storage/`. A run stores its configuration,
status, and final summary. During a run, the logger records signal phase changes, detector
samples, and traffic metrics at a configurable sample interval.

The main logged tables are:

| Table | Stored data |
|---|---|
| `runs` | Scenario, controller, duration, step, seed, configuration JSON, final summary |
| `signal_events` | Phase transitions and transition reasons |
| `detector_samples` | Controller-visible demand values |
| `traffic_metrics` | Queue lengths, completed vehicles, and mean wait samples |

Logging supports later inspection through the API endpoints `GET /api/runs` and
`GET /api/runs/{run_id}/metrics`.

## API and Dashboard

The web interface is served by FastAPI in `src/trafficlight/api/app.py`. The root route serves the
dashboard, static dashboard files are mounted under `/static`, and the API exposes health,
scenario, simulation, benchmark, run-history, and metric endpoints.

The dashboard uses a WebSocket stream at `WS /ws/simulation` for live simulation updates. Each step
message includes the active phase, elapsed phase time, signal colours, real queue lengths,
controller-visible detector demand, completed vehicles, and mean wait. The JavaScript dashboard in
`src/trafficlight/dashboard/app.js` renders these updates as a live intersection, queue meters,
detector values, and a queue-history chart.

The dashboard also includes a benchmark workflow. It posts scenario, seed, duration, and step
configuration to `POST /api/benchmarks`, receives row-level and aggregate benchmark results, then
renders the fixed-vs-adaptive table and aggregate charts.

## Benchmark and Reporting Workflow

The benchmark workflow is implemented in `src/trafficlight/simulation/benchmark.py` and
`scripts/benchmark.py`. For each scenario and seed, it runs the fixed-time controller first and
the adaptive controller second. The adaptive result stores comparison fields such as completed
vehicle difference, mean-wait improvement percentage, and max-queue improvement percentage.

Aggregate benchmark outputs include:

- Mean completed vehicles
- Standard deviation and 95% confidence interval for completed vehicles
- Mean waiting time
- Standard deviation and 95% confidence interval for waiting time
- Mean maximum queue
- Standard deviation and 95% confidence interval for maximum queue
- Total conflicting-green violations
- Improvement percentages relative to the fixed-time baseline

The final dissertation output is generated by `scripts/dissertation_results.py`. It writes
row-level CSV, aggregate summary CSV, detector-fault CSV, SVG charts, and a markdown summary under
`results/dissertation/`.

## Testing Strategy

The automated tests cover the main safety and evaluation risks:

- Controller tests verify startup state, clearance sequence, maximum green enforcement, and demand
  response.
- Safety tests verify that conflicting-green states are rejected.
- Simulation tests verify that adaptive and fixed controllers can be compared on the same seed.
- Storage tests verify SQLite logging.
- API tests verify simulation, benchmark, dashboard, and run-history endpoints.
- Benchmark/reporting tests verify CSV, aggregate statistics, and report asset generation.
- Fault tests verify detector fault behaviour.

The current suite is run with:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

The latest verification run passed with 24 tests and one Starlette TestClient deprecation warning.

## Implementation Limitations

The simulator is intentionally simplified. It models straight-through queue discharge only and
does not include turning movements, pedestrians, emergency vehicles, lane changes, weather,
detector noise distributions, vehicle classes, or calibrated real junction data. Because of this,
the implementation is suitable for evaluating the project algorithm in a controlled setting, but
not for deployment or real traffic prediction.

The dashboard is also a visualisation and experiment interface, not an operational traffic-control
system. The project remains simulation-only, with Raspberry Pi deployment, GPIO wiring, and
physical signal hardware explicitly outside the current branch scope.
