# Design and Evaluation of a Simulation-Based Adaptive Smart Traffic-Light Controller

## Abstract

This project designs, implements, and evaluates an adaptive smart traffic-light controller for a
four-way intersection in a full software simulation. The system compares an adaptive demand-based
controller with a fixed-time baseline under repeatable traffic scenarios. The simulator records
vehicle arrivals, completed vehicles, waiting time, maximum queue length, and safety violations.
It also provides a browser dashboard for live visualisation, detector-fault experiments, and
benchmark charts. Across the final 10-seed benchmark and detector-fault experiments, the adaptive
controller reduced mean waiting time in every benchmark scenario and the system recorded zero
conflicting-green violations.

## Chapter 1: Introduction

Urban intersections are points where competing traffic flows must be managed safely and
efficiently. Fixed-time traffic lights use predetermined phase durations, which makes them simple
and predictable but limits their ability to respond to changing demand. When one approach has a
long queue and another has little or no demand, a fixed cycle may waste green time and increase
waiting time.

This project investigates whether a simple adaptive controller can improve intersection
performance compared with a fixed-time baseline. The work originally considered Raspberry Pi
hardware, but the current branch deliberately uses a total software simulation. This keeps the
project measurable, repeatable, and safe while still demonstrating the core traffic-control
algorithm.

### Aim

The aim is to build and evaluate an adaptive four-way smart traffic-light controller using
repeatable simulation, live visualisation, database logging, and fixed-vs-adaptive benchmarks.

### Objectives

1. Implement a safe traffic-light phase controller for a four-way intersection.
2. Implement a fixed-time baseline controller.
3. Implement an adaptive controller that changes green duration based on detected demand.
4. Build a repeatable traffic simulator with multiple demand scenarios.
5. Log simulation runs, phase events, detector samples, and traffic metrics.
6. Provide a browser dashboard showing live signals, queues, detector values, and benchmark charts.
7. Compare fixed-time and adaptive controllers using identical traffic traces.
8. Evaluate detector-fault behaviour and safety.

### Scope

The system models North, East, South, and West approaches using two movement groups:
North/South and East/West. It includes green, amber, and all-red clearance phases. It does not
include Raspberry Pi deployment, GPIO wiring, camera detection, physical LEDs, pedestrian phases,
emergency-vehicle priority, or public-road operation.

## Chapter 2: Background and Literature Review

Traffic-signal timing affects delay, queue length, throughput, and safety at intersections.
Fixed-time control is simple but cannot react to live demand. Adaptive signal control adjusts
timing based on measured or estimated traffic conditions. The Federal Highway Administration
describes adaptive signal control as a method for adjusting signal timing to changing traffic
patterns.[^fhwa-asct]

Signal timing also depends on safety-critical phase structure. Traffic-signal guidance separates
green, yellow or amber change, and red clearance intervals.[^fhwa-timing] This supports the design
decision to model amber and all-red clearance as explicit controller states. The adaptive
algorithm in this project can change green duration, but it cannot bypass the shared safety phase
sequence.

Simulation is appropriate for this project because it allows the same traffic input to be replayed
for both controllers. This makes the comparison controlled and repeatable. SUMO is one example of
a traffic simulation system with traffic-light modelling support.[^sumo-tl] This project uses a
custom lightweight simulator instead, because it is easier to test, explain, and integrate with
the controller code.

The implementation uses Python, FastAPI, SQLite, pytest, and a static browser dashboard. FastAPI
supports typed HTTP endpoints and WebSocket communication.[^fastapi-docs][^fastapi-ws] SQLite
provides local embedded storage without an external database server.[^sqlite-wal] pytest supports
repeatable automated testing, including parametrised test cases.[^pytest-parametrize]

## Chapter 3: Requirements Specification

The system requirements are grouped into functional, safety, non-functional, data, and interface
requirements. The complete requirements table is maintained in
`docs/proposal/requirements-specification.md`.

Key requirements are:

- the controller shall model a four-way intersection;
- the controller shall start in an all-red state;
- green phases shall transition through amber and all-red before the opposing movement receives
  green;
- the system shall provide both fixed-time and adaptive controllers;
- the simulator shall generate repeatable traffic arrivals using random seeds;
- the dashboard shall show live signal state, vehicle queues, detector values, and benchmark
  results;
- the benchmark runner shall compare fixed and adaptive controllers under identical scenario,
  seed, duration, and step settings;
- the system shall record zero conflicting-green violations in benchmark and fault experiments.

The central safety requirement is:

```text
North/South green and East/West green must never be active at the same time.
```

## Chapter 4: Methodology and Implementation

The project uses an incremental software-engineering method. The safe phase model was implemented
first, followed by fixed and adaptive timing policies, the traffic simulator, persistence, API,
dashboard, benchmark runner, detector-fault experiments, and report export scripts.

The implementation is organised into four main layers:

| Layer | Purpose | Main files |
|---|---|---|
| Domain | Signal phases, controller timing, safety rules | `src/trafficlight/domain/` |
| Simulation | Queue model, traffic scenarios, faults, benchmarks | `src/trafficlight/simulation/` |
| Storage | SQLite run/event/metric logging | `src/trafficlight/storage/` |
| Interface | CLI, FastAPI endpoints, WebSocket stream, dashboard | `src/trafficlight/main.py`, `src/trafficlight/api/`, `src/trafficlight/dashboard/` |

### Phase Controller

The shared phase sequence is:

1. all-red before North/South green
2. North/South green
3. North/South amber
4. all-red before East/West green
5. East/West green
6. East/West amber

Both controllers inherit this sequence from the same base phase controller. The fixed-time
controller uses the configured fixed green time for every green phase. The adaptive controller
calculates green duration from the ratio of active movement demand to total active plus opposing
demand.

Default timing values are:

| Parameter | Value |
|---|---:|
| Minimum green | 8 seconds |
| Fixed green baseline | 20 seconds |
| Maximum green | 45 seconds |
| Amber | 3 seconds |
| All-red clearance | 2 seconds |

### Simulator

At each simulation step, the engine adds vehicle arrivals, creates a true demand snapshot, applies
detector faults if configured, advances the controller, checks for conflicting greens, discharges
vehicles from green approaches, accumulates waiting time, and records or publishes the step state.

The scenarios are:

| Scenario | Purpose |
|---|---|
| `balanced` | Similar demand on all approaches |
| `ns-heavy` | North/South demand is higher than East/West demand |
| `ew-heavy` | East/West demand is higher than North/South demand |
| `ns-burst` | Temporary North/South demand surge |
| `alternating-peak` | Demand shifts from North/South to East/West halfway through the run |

Detector-fault profiles include `none`, `ns-stuck-high`, `ew-stuck-low`, and
`all-stuck-low-midrun`.

### Dashboard and Reporting

The dashboard streams live simulation state over `WS /ws/simulation`. It displays signal phase,
signal colour, queues, detector readings, completed vehicles, mean wait, maximum queue, safety
violations, and visible vehicles. The benchmark screen posts to `POST /api/benchmarks` and renders
row-level fixed/adaptive results plus aggregate charts.

The final report artifacts are generated with:

```powershell
.\.venv\Scripts\python.exe scripts\dissertation_results.py --duration 300 --step 0.5 --seeds 10 --output-dir results\dissertation
```

## Chapter 5: Testing

The automated test suite covers controller behaviour, safety checks, simulation comparability,
SQLite logging, API endpoints, WebSocket output, benchmark aggregation, report generation, and
detector faults.

The latest verification command was:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

The suite passed with 24 tests and one Starlette TestClient deprecation warning.

Browser evidence was captured using Playwright:

- `output/playwright/dashboard-live-simulation.png`
- `output/playwright/dashboard-fault-mismatch.png`
- `output/playwright/dashboard-benchmark-results.png`

## Chapter 6: Results and Evaluation

The final benchmark used 300-second runs, 0.5-second simulation steps, and seeds 1 to 10. Each
fixed/adaptive comparison used the same scenario and seed.

The final experiment package was regenerated after correcting the simulator's arrival and waiting
time accounting. Arrivals are now sampled from the configured per-minute demand rate, and mean
wait is calculated from completed vehicles using each vehicle's recorded arrival and departure
time.

| Scenario | Fixed mean wait (s) | Adaptive mean wait (s) | Wait improvement | Fixed max queue | Adaptive max queue | Queue improvement | Completed change | Safety violations |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Balanced | 23.91 +/- 1.25 | 21.89 +/- 1.25 | +8.33% +/- 3.90 pp | 13.00 +/- 1.31 | 11.70 +/- 0.93 | +9.18% +/- 5.82 pp | +1.90 +/- 1.90 | 0 |
| NS-heavy | 43.93 +/- 3.38 | 29.51 +/- 2.37 | +32.54% +/- 4.23 pp | 44.00 +/- 5.99 | 22.90 +/- 4.83 | +48.77% +/- 4.75 pp | +41.60 +/- 3.67 | 0 |
| EW-heavy | 50.15 +/- 2.77 | 28.48 +/- 2.15 | +43.11% +/- 3.57 pp | 40.90 +/- 3.71 | 20.20 +/- 2.86 | +50.84% +/- 4.11 pp | +42.70 +/- 3.33 | 0 |
| NS-burst | 44.10 +/- 1.71 | 37.82 +/- 3.21 | +14.46% +/- 5.07 pp | 39.90 +/- 3.97 | 28.40 +/- 4.08 | +29.54% +/- 3.87 pp | +36.50 +/- 3.18 | 0 |
| Alternating peak | 54.58 +/- 3.50 | 38.09 +/- 5.24 | +30.76% +/- 6.20 pp | 38.90 +/- 3.80 | 30.70 +/- 4.79 | +21.81% +/- 6.93 pp | +23.50 +/- 2.98 | 0 |

Adaptive control reduced mean waiting time in all five scenarios. It also completed more vehicles
in all five scenarios. Maximum queue length improved in all five scenarios.

Detector-fault experiments used the NS-heavy scenario with the same duration, step size, and seed
set.

| Fault profile | Runs | Mean completed | Mean wait (s) | Mean max queue | Safety violations |
|---|---:|---:|---:|---:|---:|
| none | 10 | 196.50 | 29.51 | 22.90 | 0 |
| ns-stuck-high | 10 | 198.40 | 26.52 | 17.40 | 0 |
| ew-stuck-low | 10 | 197.50 | 24.29 | 17.30 | 0 |
| all-stuck-low-midrun | 10 | 160.60 | 34.18 | 41.00 | 0 |

The all-stuck-low-midrun profile caused the worst performance degradation, with lower completed
vehicles and higher mean wait. However, all detector-fault experiments still recorded zero
conflicting-green violations.

## Chapter 7: Discussion

The results support the project claim that adaptive timing can reduce waiting time compared with a
fixed-time baseline under unequal or changing traffic demand. The improvement is strongest in the
EW-heavy and NS-heavy scenarios, both of which contain clear demand imbalance.

The queue results show that a single metric is not enough to evaluate controller behaviour.
Adaptive control improved completed-vehicle wait, maximum queue, and throughput across the
benchmark set, while detector-fault experiments showed that poor detector input can still reduce
performance.

The detector-fault results show that bad demand input can reduce performance. This is expected for
an adaptive controller. The important safety result is that detector faults do not directly command
the signal outputs, so the safety phase model remains intact.

## Chapter 8: Conclusion

The project successfully implemented a simulation-only adaptive smart traffic-light controller and
evaluated it against a fixed-time baseline. The system includes a safe phase controller, adaptive
green-time policy, repeatable traffic scenarios, SQLite logging, FastAPI API, WebSocket dashboard,
benchmark runner, detector-fault simulation, CSV/SVG export, and automated tests.

The final experiments show that the adaptive controller reduced mean waiting time by approximately
8.33% to 43.11% across the tested scenarios and completed more vehicles than the fixed-time
baseline. The project also maintained zero conflicting-green violations across the benchmark and
detector-fault experiments.

## Limitations and Future Work

The simulator is simplified. It does not model turning movements, pedestrians, lane changes,
vehicle classes, weather, real detector noise, emergency vehicles, or calibrated field data. The
findings should therefore be interpreted as evidence for the implemented simulation, not as direct
predictions for a real road junction.

Future work could add:

- calibrated traffic-flow data;
- pedestrian request phases;
- emergency-priority events;
- richer detector noise models;
- sensitivity tests for discharge headway and arrival rates;
- SUMO-based validation;
- optional hardware adapters if the project later returns to Raspberry Pi demonstration.

## Evidence and Artifacts

Generated dissertation results:

- `results/dissertation/results_summary.md`
- `results/dissertation/benchmark_rows.csv`
- `results/dissertation/benchmark_summary.csv`
- `results/dissertation/failure_modes.csv`
- `results/dissertation/mean_wait.svg`
- `results/dissertation/max_queue.svg`
- `results/dissertation/completed.svg`

Dashboard screenshots:

- `output/playwright/dashboard-live-simulation.png`
- `output/playwright/dashboard-fault-mismatch.png`
- `output/playwright/dashboard-benchmark-results.png`

Supporting draft sections:

- `docs/proposal/background-literature-review.md`
- `docs/proposal/requirements-specification.md`
- `docs/proposal/methodology-implementation.md`
- `docs/proposal/results-evaluation.md`

[^fhwa-asct]: Federal Highway Administration, "Adaptive Signal Control Technology",
    https://www.fhwa.dot.gov/innovation/everydaycounts/edc-1/asct.cfm
[^fhwa-timing]: Federal Highway Administration, "Traffic Signal Timing Manual: Chapter 5",
    https://ops.fhwa.dot.gov/publications/fhwahop08024/chapter5.htm
[^sumo-tl]: Eclipse SUMO documentation, "Traffic Lights",
    https://sumo.dlr.de/docs/Simulation/Traffic_Lights.html
[^fastapi-docs]: FastAPI documentation, "FastAPI",
    https://fastapi.tiangolo.com/
[^fastapi-ws]: FastAPI documentation, "WebSockets",
    https://fastapi.tiangolo.com/advanced/websockets/
[^sqlite-wal]: SQLite documentation, "Write-Ahead Logging",
    https://www.sqlite.org/wal.html
[^pytest-parametrize]: pytest documentation, "Parametrizing tests",
    https://docs.pytest.org/en/stable/example/parametrize.html
