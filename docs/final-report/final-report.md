# Design and Evaluation of a Simulation-Based Adaptive Smart Traffic-Light Controller

**Programme:** Final-Year Project  
**Project Type:** Software simulation and evaluation  
**Implementation Branch:** `simulation-only`  
**Date:** 9 September 2026

## Declaration

This report describes a simulation-based adaptive traffic-light control project developed for
academic evaluation. The implementation is not intended for use on public roads or as certified
traffic-control equipment.

## Abstract

This project designs, implements, and evaluates an adaptive smart traffic-light controller for a
four-way intersection using a full software simulation. The controller is compared with a
fixed-time baseline under repeatable traffic scenarios. The simulator records arrivals, completed
vehicles, waiting time, maximum queue length, detector-fault behaviour, and safety violations. A
browser dashboard provides live visualisation of signal phases, vehicle queues, detector values,
benchmark tables, and aggregate charts.

The final benchmark used five traffic scenarios, 10 random seeds, 300-second runs, and a
0.5-second simulation step. Adaptive control reduced mean waiting time in every tested scenario,
with improvements from 5.18% to 7.24%. It also completed more vehicles than the fixed-time
baseline in every scenario. The controller recorded zero conflicting-green violations across the
benchmark and detector-fault experiments. The results support the project claim that adaptive
green-time control can improve performance in the implemented simulation while preserving the
shared phase-safety constraints.

## Table of Contents

1. Introduction
2. Background and Literature Review
3. Requirements Specification
4. Methodology and Implementation
5. Testing and Verification
6. Results and Evaluation
7. Discussion
8. Conclusion
9. Limitations and Future Work
10. References
11. Appendices

## List of Figures

| Figure | Description | Source artifact |
|---|---|---|
| Figure 1 | Live dashboard simulation with visible vehicles | `output/playwright/dashboard-live-simulation.png` |
| Figure 2 | Detector-fault dashboard showing demand mismatch | `output/playwright/dashboard-fault-mismatch.png` |
| Figure 3 | Dashboard benchmark table and aggregate charts | `output/playwright/dashboard-benchmark-results.png` |
| Figure 4 | Mean waiting-time comparison chart | `results/dissertation/mean_wait.svg` |
| Figure 5 | Maximum queue comparison chart | `results/dissertation/max_queue.svg` |
| Figure 6 | Completed vehicles comparison chart | `results/dissertation/completed.svg` |

## List of Tables

| Table | Description |
|---|---|
| Table 1 | Main system objectives |
| Table 2 | Implementation layers |
| Table 3 | Core functional requirements |
| Table 4 | Traffic scenarios |
| Table 5 | Detector fault profiles |
| Table 6 | Benchmark results |
| Table 7 | Detector-fault results |

## Chapter 1: Introduction

### 1.1 Background

Urban intersections are shared spaces where multiple traffic streams compete for right of way.
Traffic-light controllers must allocate movement time efficiently while preventing unsafe
conflicts. Conventional fixed-time traffic lights follow predetermined timings, which makes them
simple and predictable. However, fixed timings cannot react when traffic demand changes from one
approach to another.

An adaptive traffic-light controller can respond to measured traffic demand by adjusting green
duration. For example, if North/South queues are much longer than East/West queues, the controller
can allocate more green time to North/South traffic while still preserving minimum and maximum
green limits. This project investigates that idea in a controlled software simulation.

### 1.2 Problem Statement

Fixed-time signal control can waste green time when demand is uneven or changing. A fixed-time
phase may continue serving a low-demand approach while longer queues build on another approach.
The problem is to design a controller that responds to demand without violating signal-safety
rules.

### 1.3 Aim

The aim is to build and evaluate an adaptive four-way smart traffic-light controller using
repeatable simulation, live visualisation, database logging, and fixed-vs-adaptive benchmarks.

### 1.4 Objectives

| No. | Objective |
|---:|---|
| 1 | Implement a safe traffic-light phase controller for a four-way intersection. |
| 2 | Implement a fixed-time baseline controller. |
| 3 | Implement an adaptive controller that changes green duration based on detected demand. |
| 4 | Build a repeatable traffic simulator with multiple demand scenarios. |
| 5 | Log simulation runs, phase events, detector samples, and traffic metrics. |
| 6 | Provide a browser dashboard showing signals, queues, detector values, and benchmark charts. |
| 7 | Compare fixed-time and adaptive controllers using identical traffic traces. |
| 8 | Evaluate detector-fault behaviour and signal safety. |

### 1.5 Scope

The system models a single four-way intersection with North, East, South, and West approaches.
North/South and East/West are treated as opposing movement groups. The controller includes green,
amber, and all-red clearance states.

The current scope excludes Raspberry Pi deployment, GPIO wiring, physical LEDs, camera hardware,
pedestrian phases, emergency-vehicle priority, and public-road operation. The project is an
academic simulation and evaluation system.

## Chapter 2: Background and Literature Review

### 2.1 Fixed-Time Signal Control

Fixed-time traffic-light control uses predetermined timings for each phase. This provides a clear
baseline because the controller does not depend on live demand. In this project, the fixed-time
baseline uses the same safety phase sequence as the adaptive controller, but every green phase
uses the configured fixed duration.

### 2.2 Adaptive Signal Control

Adaptive signal control changes timing in response to traffic conditions. The Federal Highway
Administration describes adaptive signal control technology as a way to adjust signal timing to
changing traffic patterns.[^fhwa-asct] This project follows the same broad concept but applies it
inside a lightweight academic simulator.

The adaptive controller uses detected queue demand to choose a target green time between minimum
and maximum limits. It is intentionally transparent rather than machine-learning based, making the
decision process easier to inspect and defend.

### 2.3 Signal Timing and Safety

Signal timing includes more than green allocation. FHWA traffic-signal timing guidance discusses
minimum green, maximum green, yellow-change, and red-clearance intervals as separate timing
elements.[^fhwa-timing] This supports the project's explicit phase model:

```text
all-red -> green -> amber -> all-red -> opposing green
```

The project separates adaptive timing from signal safety. Adaptive logic decides when a green
phase should end, but it cannot skip amber or all-red clearance.

### 2.4 Simulation-Based Evaluation

Simulation allows controlled comparison between controllers. The same random seed can be used for
both fixed-time and adaptive runs, ensuring both controllers receive the same arrival trace. This
is important because otherwise a controller could appear better simply because it received easier
traffic input.

Traffic simulation is also widely used in transport research. SUMO provides traffic-light
modelling and supports simulation of signal control algorithms.[^sumo-tl] This project uses a
custom simulator because it is smaller, easier to test, and closely aligned with the project
requirements.

### 2.5 Software Tools

FastAPI is used for HTTP and WebSocket interfaces. It supports typed request handling and OpenAPI
documentation for HTTP endpoints.[^fastapi-docs] It also supports WebSocket communication, which
is used by the live dashboard.[^fastapi-ws] SQLite is used as an embedded database for local run
logging.[^sqlite-wal] pytest is used for automated testing and supports parametrised test cases
for repeated checks across scenarios.[^pytest-parametrize]

## Chapter 3: Requirements Specification

### 3.1 System Boundary

The system includes the controller logic, traffic simulator, fault injection, SQLite logging,
FastAPI API, browser dashboard, benchmark runner, and report export scripts. It does not include
real traffic-light hardware.

### 3.2 Core Functional Requirements

| ID | Requirement |
|---|---|
| FR-01 | The system shall model a four-way intersection with North, East, South, and West approaches. |
| FR-02 | The controller shall support North/South and East/West movement groups. |
| FR-03 | The controller shall start in an all-red state. |
| FR-04 | The controller shall transition through green, amber, and all-red clearance states. |
| FR-05 | The system shall provide a fixed-time baseline controller. |
| FR-06 | The system shall provide an adaptive demand-based controller. |
| FR-07 | The adaptive controller shall enforce minimum and maximum green durations. |
| FR-08 | The simulator shall generate repeatable arrivals using scenario configuration and seeds. |
| FR-09 | The simulator shall track arrivals, departures, waiting time, queue length, and throughput. |
| FR-10 | The system shall include balanced, asymmetric, burst, and changing-demand scenarios. |
| FR-11 | The system shall support stuck-high and stuck-low detector fault profiles. |
| FR-12 | The dashboard shall show live signals, queues, vehicles, detector values, and benchmark results. |
| FR-13 | The benchmark runner shall export row-level and aggregate CSV results. |
| FR-14 | The reporting workflow shall generate SVG charts and markdown summaries. |

### 3.3 Safety Requirements

| ID | Requirement |
|---|---|
| SR-01 | North/South green and East/West green shall never be active at the same time. |
| SR-02 | Every applied signal state shall pass through the safety check. |
| SR-03 | Adaptive timing shall not bypass amber or all-red clearance states. |
| SR-04 | Detector faults shall not directly command signal colours. |
| SR-05 | The safety target for benchmark and fault experiments shall be zero conflicting-green violations. |

### 3.4 Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-01 | The system shall run on a normal laptop without physical hardware. |
| NFR-02 | Experiments shall be repeatable using deterministic seeds. |
| NFR-03 | Controller logic shall remain separate from dashboard and persistence logic. |
| NFR-04 | The system shall support automated regression testing. |
| NFR-05 | Result artifacts shall be reproducible from command-line scripts. |

## Chapter 4: Methodology and Implementation

### 4.1 Development Approach

The project was implemented incrementally. The safe phase controller was built first, followed by
the fixed-time baseline, adaptive timing policy, simulator, storage, API, dashboard, benchmarks,
fault experiments, and report export workflow.

### 4.2 Architecture

| Layer | Purpose | Main files |
|---|---|---|
| Domain | Signal phases, controller timing, safety rules | `src/trafficlight/domain/` |
| Simulation | Queue model, traffic scenarios, faults, benchmarks | `src/trafficlight/simulation/` |
| Storage | SQLite run/event/metric logging | `src/trafficlight/storage/` |
| Interface | CLI, FastAPI endpoints, WebSocket stream, dashboard | `src/trafficlight/main.py`, `src/trafficlight/api/`, `src/trafficlight/dashboard/` |

### 4.3 Controller Design

Both controllers share the same base phase sequence:

1. all-red before North/South green
2. North/South green
3. North/South amber
4. all-red before East/West green
5. East/West green
6. East/West amber

The fixed-time controller uses the configured fixed green duration. The adaptive controller
calculates target green duration using the active movement group's share of total demand. The
adaptive value is clamped between minimum and maximum green limits.

| Parameter | Value |
|---|---:|
| Minimum green | 8 seconds |
| Fixed green baseline | 20 seconds |
| Maximum green | 45 seconds |
| Amber | 3 seconds |
| All-red clearance | 2 seconds |

### 4.4 Simulation Engine

The simulator advances in discrete time steps. At each step, it adds arrivals, applies detector
faults if configured, advances the controller, checks safety, discharges vehicles on green
approaches, accumulates waiting time, logs metrics, and sends dashboard updates.

Each approach tracks:

- current queue length;
- total arrivals;
- total departures;
- accumulated waiting time;
- arrival and discharge credits.

### 4.5 Scenarios

| Scenario | Description |
|---|---|
| `balanced` | Similar demand on all approaches |
| `ns-heavy` | North/South demand is much higher than East/West |
| `ew-heavy` | East/West demand is much higher than North/South |
| `ns-burst` | A short North/South surge during moderate demand |
| `alternating-peak` | Demand shifts from North/South to East/West during the run |

### 4.6 Detector Faults

| Fault profile | Behaviour |
|---|---|
| `none` | No detector fault |
| `ns-stuck-high` | North/South detector demand is forced high |
| `ew-stuck-low` | East/West detector demand is forced to zero |
| `all-stuck-low-midrun` | All detector readings become zero halfway through the run |

### 4.7 Dashboard

The dashboard is a static HTML/CSS/JavaScript interface served by FastAPI. It uses WebSocket
messages for live simulation updates and HTTP requests for benchmark execution. It visualises
signal lamps, queue meters, detector values, visible vehicles, run history, benchmark tables, and
aggregate charts.

### 4.8 Reporting Workflow

The final result package is generated with:

```powershell
.\.venv\Scripts\python.exe scripts\dissertation_results.py --duration 300 --step 0.5 --seeds 10 --output-dir results\dissertation
```

The script writes row-level benchmark data, aggregate benchmark data, detector-fault data, SVG
charts, and a markdown result summary.

## Chapter 5: Testing and Verification

The automated test suite covers:

- controller startup and phase transitions;
- conflicting-green rejection;
- adaptive maximum-green enforcement;
- adaptive demand response;
- simulation comparability across identical seeds;
- SQLite logging;
- API and WebSocket behaviour;
- benchmark aggregation and report generation;
- detector fault behaviour.

Verification command:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Latest result:

```text
22 passed, 1 warning
```

The warning is a Starlette TestClient deprecation warning and does not indicate a project test
failure.

## Chapter 6: Results and Evaluation

### 6.1 Experiment Configuration

| Setting | Value |
|---|---|
| Duration per run | 300 seconds |
| Simulation step | 0.5 seconds |
| Random seeds | 1 to 10 |
| Controllers | Fixed-time baseline and adaptive demand controller |
| Benchmark scenarios | balanced, ns-heavy, ew-heavy, ns-burst, alternating-peak |

### 6.2 Fixed-Time vs Adaptive Results

| Scenario | Fixed mean wait (s) | Adaptive mean wait (s) | Wait improvement | Fixed max queue | Adaptive max queue | Queue improvement | Completed change | Safety violations |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Balanced | 265.27 +/- 6.02 | 251.50 +/- 5.42 | +5.18% +/- 0.29 pp | 99.40 +/- 2.40 | 98.20 +/- 1.89 | +1.17% +/- 0.89 pp | +8.00 +/- 0.51 | 0 |
| NS-heavy | 281.27 +/- 4.43 | 263.76 +/- 4.26 | +6.22% +/- 0.59 pp | 151.90 +/- 2.90 | 137.50 +/- 2.58 | +9.48% +/- 0.49 pp | +9.80 +/- 1.09 | 0 |
| EW-heavy | 290.81 +/- 5.30 | 271.35 +/- 4.59 | +6.68% +/- 0.39 pp | 152.90 +/- 3.45 | 135.70 +/- 3.25 | +11.26% +/- 0.31 pp | +10.60 +/- 0.67 | 0 |
| NS-burst | 287.02 +/- 6.49 | 271.31 +/- 6.20 | +5.47% +/- 0.42 pp | 131.10 +/- 3.01 | 120.90 +/- 2.90 | +7.78% +/- 0.67 pp | +8.50 +/- 0.67 | 0 |
| Alternating peak | 301.63 +/- 5.75 | 279.81 +/- 5.88 | +7.24% +/- 0.53 pp | 115.40 +/- 2.76 | 118.40 +/- 2.55 | -2.65% +/- 1.80 pp | +12.20 +/- 1.09 | 0 |

Adaptive control reduced mean waiting time in all five scenarios and completed more vehicles in
all five scenarios. Maximum queue length improved in four scenarios. The alternating-peak scenario
showed a small maximum-queue increase, but still had lower mean waiting time and higher completed
vehicles.

### 6.3 Detector-Fault Results

| Fault profile | Runs | Mean completed | Mean wait (s) | Mean max queue | Safety violations |
|---|---:|---:|---:|---:|---:|
| none | 10 | 225.80 | 263.76 | 137.50 | 0 |
| ns-stuck-high | 10 | 228.40 | 258.04 | 131.20 | 0 |
| ew-stuck-low | 10 | 232.00 | 253.49 | 105.40 | 0 |
| all-stuck-low-midrun | 10 | 196.60 | 314.48 | 146.90 | 0 |

The all-stuck-low-midrun fault produced the worst performance degradation. However, all fault
experiments still recorded zero conflicting-green violations.

## Chapter 7: Discussion

The results support the central project claim. Adaptive control improved mean waiting time under
balanced, asymmetric, burst, and changing-demand conditions while preserving safety. The
controller performed especially well in the EW-heavy and alternating-peak scenarios, where the
demand imbalance was strongest.

The results also show that performance must be evaluated using more than one metric. In the
alternating-peak scenario, adaptive control reduced mean wait and increased completed vehicles,
but the maximum queue rose slightly. This indicates a tradeoff between average delay and peak
queue length during a demand transition.

Detector faults affected performance but did not create unsafe signal states. This is because
faults change only the demand input seen by the controller. They do not bypass the phase
controller or directly set lamp colours.

## Chapter 8: Conclusion

The project successfully delivered a simulation-only adaptive smart traffic-light controller. It
includes a safe phase state machine, fixed-time baseline, adaptive demand-based timing,
repeatable scenarios, detector fault simulation, SQLite logging, FastAPI API, WebSocket dashboard,
benchmark runner, report exports, and automated tests.

The final experiments show that adaptive control reduced mean waiting time by 5.18% to 7.24%
across the tested scenarios. The adaptive controller also completed more vehicles than the
fixed-time baseline in every scenario. Across all benchmark and detector-fault experiments, the
system recorded zero conflicting-green violations.

## Chapter 9: Limitations and Future Work

The project uses a simplified traffic simulator. It does not model turning movements,
pedestrians, emergency vehicles, lane changes, weather, vehicle classes, realistic driver
behaviour, calibrated road geometry, or real detector noise. The results should therefore be
interpreted as evidence for the implemented simulation rather than direct predictions for a real
road junction.

Future work could add:

- pedestrian request phases;
- emergency-priority simulation;
- richer detector noise models;
- sensitivity tests for arrival rate and discharge headway;
- calibrated field or model-road data;
- SUMO-based validation;
- optional hardware adapters if the project later returns to Raspberry Pi demonstration.

## References

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

## Appendices

### Appendix A: Generated Result Artifacts

| Artifact | Purpose |
|---|---|
| `results/dissertation/results_summary.md` | Markdown experiment summary |
| `results/dissertation/benchmark_rows.csv` | Row-level fixed/adaptive benchmark data |
| `results/dissertation/benchmark_summary.csv` | Aggregate benchmark statistics |
| `results/dissertation/failure_modes.csv` | Detector-fault experiment data |
| `results/dissertation/mean_wait.svg` | Mean waiting-time chart |
| `results/dissertation/max_queue.svg` | Maximum queue chart |
| `results/dissertation/completed.svg` | Completed vehicles chart |

### Appendix B: Dashboard Evidence

| Artifact | Purpose |
|---|---|
| `output/playwright/dashboard-live-simulation.png` | Live simulation with visible vehicles |
| `output/playwright/dashboard-fault-mismatch.png` | Detector fault showing queue/demand mismatch |
| `output/playwright/dashboard-benchmark-results.png` | Benchmark results table and aggregate charts |

### Appendix C: Important Commands

Run tests:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Run dashboard:

```powershell
.\.venv\Scripts\python.exe -m uvicorn trafficlight.api.app:app --host 127.0.0.1 --port 8000
```

Generate dissertation results:

```powershell
.\.venv\Scripts\python.exe scripts\dissertation_results.py --duration 300 --step 0.5 --seeds 10 --output-dir results\dissertation
```
