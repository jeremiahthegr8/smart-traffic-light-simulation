# Requirements Specification Draft

This document defines the requirements for the simulation-only adaptive traffic-light system. The
requirements are written to match the implemented project scope and to support traceability from
project objectives to tests, generated results, and dashboard evidence.

## System Boundary

The system is a software simulation of a four-way traffic-light controller. It includes the
controller logic, traffic simulator, fault injection, data logging, API, dashboard, benchmark
runner, and report export scripts.

The current branch does not include Raspberry Pi deployment, GPIO wiring, physical LEDs, camera
hardware, pedestrian phases, emergency vehicle detection, or public-road operation.

## Stakeholders

| Stakeholder | Interest |
|---|---|
| Student developer | Build, test, explain, and defend the final-year project |
| Supervisor/examiner | Review architecture, correctness, safety, evidence, and results |
| Demonstration user | Run the dashboard and observe controller behaviour |
| Future maintainer | Extend the simulator, add hardware adapters, or improve experiments |

## Functional Requirements

| ID | Requirement | Acceptance evidence |
|---|---|---|
| FR-01 | The system shall model a four-way intersection with North, East, South, and West approaches. | Scenarios and dashboard render all four approaches. |
| FR-02 | The controller shall support North/South and East/West movement groups. | `SignalState.for_group` and dashboard signal state display. |
| FR-03 | The controller shall start in an all-red state. | `test_controller_starts_all_red`. |
| FR-04 | The controller shall transition through green, amber, and all-red clearance states before serving the opposing movement. | `test_fixed_time_controller_uses_clearance_sequence`. |
| FR-05 | The system shall provide a fixed-time baseline controller. | `FixedTimeController` and benchmark row output. |
| FR-06 | The system shall provide an adaptive controller that changes green duration based on detected demand. | `test_adaptive_target_green_increases_with_active_demand`. |
| FR-07 | The adaptive controller shall enforce minimum and maximum green durations. | `test_adaptive_controller_never_exceeds_max_green`; timing config validation. |
| FR-08 | The simulator shall generate repeatable vehicle arrivals using scenario configuration and random seeds. | Fixed/adaptive benchmark rows have matching arrivals for the same seed. |
| FR-09 | The simulator shall track arrivals, departures, waiting time, queue length, throughput, and safety violations. | Simulation summary and benchmark CSV fields. |
| FR-10 | The system shall include multiple traffic scenarios covering balanced, asymmetric, burst, and changing demand. | `SCENARIOS` contains `balanced`, `ns-heavy`, `ew-heavy`, `ns-burst`, and `alternating-peak`. |
| FR-11 | The system shall support detector fault profiles for stuck-high and stuck-low demand readings. | `/api/fault-profiles`, `run_failure_modes`, and fault tests. |
| FR-12 | The simulator shall expose true queue values and controller-visible detector demand separately. | WebSocket step payload includes `queues`, `true_demand`, and `demand`. |
| FR-13 | The command line interface shall run a single simulation and print a JSON summary. | `python -m trafficlight.main ...`. |
| FR-14 | The API shall expose health, scenario, simulation, benchmark, run-history, and run-metric endpoints. | `tests/unit/test_api.py`. |
| FR-15 | The dashboard shall stream live simulation state over WebSocket. | `WS /ws/simulation` and dashboard live simulation screenshot. |
| FR-16 | The dashboard shall display signal colour, phase, queue metrics, detector readings, completed vehicles, mean wait, max queue, and safety violations. | Dashboard implementation and screenshots in `output/playwright/`. |
| FR-17 | The dashboard shall show visible queued and moving vehicles in the intersection view. | `dashboard-live-simulation.png`. |
| FR-18 | The dashboard shall allow selection of controller, scenario, duration, step size, seed, and fault profile. | Dashboard controls in `index.html`. |
| FR-19 | The dashboard shall run fixed-vs-adaptive benchmarks and display row-level results. | `dashboard-benchmark-results.png`. |
| FR-20 | The dashboard shall display aggregate benchmark charts for mean wait and maximum queue. | Dashboard benchmark screenshot and chart rendering checks. |
| FR-21 | The benchmark runner shall compare fixed-time and adaptive controllers on identical scenario, seed, duration, and step settings. | `test_benchmark_runs_fixed_and_adaptive_on_same_trace`. |
| FR-22 | The benchmark runner shall export row-level CSV results. | `results/dissertation/benchmark_rows.csv`. |
| FR-23 | The benchmark runner shall export aggregate CSV results with mean, standard deviation, and 95% confidence interval fields. | `results/dissertation/benchmark_summary.csv`; reporting tests. |
| FR-24 | The report generator shall export SVG charts for mean wait, maximum queue, and completed vehicles. | `results/dissertation/mean_wait.svg`, `max_queue.svg`, and `completed.svg`. |
| FR-25 | The dissertation results script shall generate all final result artifacts in one command. | `scripts/dissertation_results.py`. |

## Safety Requirements

| ID | Requirement | Acceptance evidence |
|---|---|---|
| SR-01 | The system shall never allow North/South green and East/West green at the same time. | `assert_no_conflicting_greens`; final experiments report 0 violations. |
| SR-02 | The system shall reject conflicting-green signal states in automated tests. | `test_conflicting_greens_are_rejected`. |
| SR-03 | The controller shall pass every applied signal state through the safety check before output. | `BasePhaseController._apply_phase`. |
| SR-04 | Adaptive timing shall not bypass amber or all-red clearance states. | Shared `BasePhaseController` transition map. |
| SR-05 | Detector faults shall not directly command signal colours. | Faults only modify `DemandSnapshot`; output remains controlled by phase machine. |
| SR-06 | The safety target for every benchmark and failure-mode experiment shall be zero conflicting-green violations. | `results/dissertation/results_summary.md`. |

## Non-Functional Requirements

| ID | Requirement | Acceptance evidence |
|---|---|---|
| NFR-01 | The system shall run on a normal laptop without physical traffic-light hardware. | Simulation-only branch and README setup. |
| NFR-02 | The system shall use deterministic seeds for repeatable experiments. | Benchmark seed parameters and generated 10-seed result set. |
| NFR-03 | The system shall keep controller logic separate from interface and persistence layers. | Domain, simulation, storage, API, and dashboard package structure. |
| NFR-04 | The system shall support automated regression testing. | pytest suite. |
| NFR-05 | The system shall store local run history without requiring an external database service. | SQLite storage layer. |
| NFR-06 | The dashboard shall be usable in a browser without a frontend build process. | Static HTML/CSS/JavaScript dashboard. |
| NFR-07 | Generated result artifacts shall be reproducible from scripts. | `scripts/benchmark.py`, `scripts/failure_modes.py`, and `scripts/dissertation_results.py`. |
| NFR-08 | The system shall avoid public-road deployment claims. | Scope and limitations in report drafts. |

## Data Requirements

| ID | Requirement | Data fields |
|---|---|---|
| DR-01 | Each simulation run shall record its configuration. | scenario, controller, duration, step, seed, fault profile |
| DR-02 | Each simulation summary shall include core evaluation metrics. | arrivals, completed, throughput, mean wait, max queue, safety violations |
| DR-03 | Logged detector samples shall store controller-visible demand by approach. | north, east, south, west demand |
| DR-04 | Logged traffic metrics shall store queue values by approach. | north, east, south, west queue |
| DR-05 | Benchmark rows shall store fixed/adaptive comparisons for each scenario and seed. | completed delta, wait improvement, max queue improvement |
| DR-06 | Aggregate benchmark rows shall include statistical spread. | standard deviation and 95% confidence interval fields |

## Interface Requirements

| ID | Requirement | Interface |
|---|---|---|
| IR-01 | Users shall be able to run simulations from the command line. | `python -m trafficlight.main` |
| IR-02 | Users shall be able to run benchmarks from the command line. | `python scripts/benchmark.py` |
| IR-03 | Users shall be able to generate dissertation artifacts from the command line. | `python scripts/dissertation_results.py` |
| IR-04 | API clients shall be able to run simulations through JSON requests. | `POST /api/simulations` |
| IR-05 | API clients shall be able to run fixed/adaptive benchmarks through JSON requests. | `POST /api/benchmarks` |
| IR-06 | Browser users shall be able to view live simulation state. | `GET /` and `WS /ws/simulation` |
| IR-07 | Browser users shall be able to inspect recent persisted runs. | `GET /api/runs` |

## Traceability Matrix

| Objective | Linked requirements | Evidence |
|---|---|---|
| Implement safe traffic-control logic | FR-03, FR-04, SR-01 to SR-06 | safety/controller tests, result summary |
| Implement fixed-time baseline | FR-05, FR-21 | benchmark rows and API tests |
| Implement adaptive demand control | FR-06, FR-07, FR-21 | controller tests and benchmark results |
| Support total simulation | FR-08 to FR-12, NFR-01 | simulator, scenarios, fault profiles |
| Provide live visualisation | FR-15 to FR-20, IR-06 | dashboard screenshots |
| Record experiment data | FR-22 to FR-25, DR-01 to DR-06 | CSV/SVG/markdown artifacts |
| Evaluate fixed vs adaptive control | FR-21 to FR-25 | dissertation result package |
| Demonstrate robustness to detector faults | FR-11, FR-12, SR-05, SR-06 | failure-mode CSV and fault screenshot |

## Acceptance Criteria

The project is acceptable for the current simulation-only scope when:

1. The pytest suite passes.
2. A live dashboard simulation shows signal phases, queue values, detector values, and vehicles.
3. A detector-fault dashboard run visibly separates true queue values from faulty detector demand.
4. The dissertation results script generates benchmark, failure-mode, chart, and markdown outputs.
5. The final benchmark and failure-mode experiments record zero conflicting-green violations.
6. The results chapter can cite generated CSV, SVG, markdown, and screenshot artifacts.

The current implementation satisfies these criteria for the MVP scope.
