# Demonstration Script Draft

This script is for a short project demonstration or viva walkthrough. It assumes the project is
presented as a complete software simulation rather than a Raspberry Pi hardware prototype.

## Demo Goal

Show that the project implements a safe adaptive traffic-light controller, runs fully in
simulation, visualises traffic in a browser dashboard, and produces repeatable fixed-vs-adaptive
evaluation results.

## Recommended Duration

Aim for 6 to 8 minutes:

| Time | Segment |
|---:|---|
| 0:00-0:45 | Introduce the problem and project scope |
| 0:45-1:45 | Explain the controller and safety design |
| 1:45-3:00 | Show live dashboard simulation |
| 3:00-4:00 | Show detector-fault behaviour |
| 4:00-5:30 | Show benchmark results and charts |
| 5:30-6:30 | Show automated tests and generated report artifacts |
| 6:30-8:00 | Conclude and answer questions |

## Before the Demo

Open a terminal in the project folder:

```powershell
cd C:\Code\school\FinalYear\TrafficLight
```

Confirm the branch:

```powershell
git branch --show-current
```

Expected branch:

```text
simulation-only
```

Run tests if there is time:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Expected result:

```text
24 passed, 1 warning
```

Start the dashboard:

```powershell
.\.venv\Scripts\python.exe -m uvicorn trafficlight.api.app:app --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000/
```

If port 8000 is busy, use port 8001:

```powershell
.\.venv\Scripts\python.exe -m uvicorn trafficlight.api.app:app --host 127.0.0.1 --port 8001
```

## Segment 1: Introduction

Say:

> My project is a simulation-based adaptive smart traffic-light controller for a four-way
> intersection. The aim is to compare an adaptive demand-based controller with a fixed-time
> baseline using repeatable experiments. I moved the final scope away from physical hardware so
> the project can focus on the controller algorithm, dashboard, safety tests, and quantitative
> evaluation.

Show:

- [README.md](/c:/Code/school/FinalYear/TrafficLight/README.md)
- [implementation-plan.md](/c:/Code/school/FinalYear/TrafficLight/docs/proposal/implementation-plan.md)

Key point:

> The hardware is not the main contribution. The main contribution is the tested simulation,
> adaptive timing logic, and measured comparison against fixed-time control.

## Segment 2: Controller and Safety Design

Open:

- [controller.py](/c:/Code/school/FinalYear/TrafficLight/src/trafficlight/domain/controller.py)
- [safety.py](/c:/Code/school/FinalYear/TrafficLight/src/trafficlight/domain/safety.py)

Say:

> The controller uses two movement groups: North/South and East/West. Both the fixed-time and
> adaptive controllers share the same safe phase sequence. The sequence always goes through amber
> and all-red clearance before serving the opposing direction.

Explain the phase order:

```text
all-red -> NS green -> NS amber -> all-red -> EW green -> EW amber -> all-red
```

Say:

> The adaptive controller only changes how long the green phase lasts. It cannot skip the amber or
> all-red states. Every signal state is checked so North/South green and East/West green cannot be
> active at the same time.

Key phrase:

> The safety target is zero conflicting-green violations, not just a low number.

## Segment 3: Live Dashboard Simulation

In the dashboard, use:

| Control | Value |
|---|---|
| Controller | Adaptive |
| Scenario | NS-heavy |
| Fault profile | None |
| Duration | 120 |
| Step | 1 |
| Seed | 42 |

Click `Run`.

Point out:

- active phase and elapsed phase time
- visible queued vehicles
- moving vehicles during green
- queue values for each direction
- detector readings
- completed vehicles
- mean wait
- safety violations

Say:

> This dashboard is not just a drawing. It is connected to the simulator through a WebSocket. Each
> simulation step sends the current phase, signal colours, queue lengths, detector demand,
> completed vehicles, and waiting-time metrics.

Screenshot fallback:

- `output/playwright/dashboard-live-simulation.png`

## Segment 4: Detector-Fault Behaviour

In the dashboard, use:

| Control | Value |
|---|---|
| Controller | Adaptive |
| Scenario | NS-heavy |
| Fault profile | NS stuck high |
| Duration | 120 |
| Step | 1 |
| Seed | 42 |

Click `Run`.

Point out:

- North/South detector values become stuck at 80
- true queue values remain lower
- the controller still follows safe signal phases
- safety violations remain 0

Say:

> Detector faults change what the controller thinks the demand is, but they do not directly set
> the lights. This separates performance robustness from signal safety. A bad detector can hurt
> performance, but the phase machine still prevents conflicting greens.

Screenshot fallback:

- `output/playwright/dashboard-fault-mismatch.png`

## Segment 5: Benchmark Results

In the dashboard, use:

| Control | Value |
|---|---|
| Duration | 300 |
| Step | 0.5 |
| Seed | 1 |
| Benchmark seeds | 10 |

Click `Benchmark`.

Point out:

- 100 row-level runs: 5 scenarios x 10 seeds x 2 controllers
- fixed and adaptive rows use matching seeds
- wait improvement column
- aggregate mean-wait chart
- aggregate max-queue chart
- zero safety violations

Say:

> The benchmark is repeatable because fixed and adaptive runs use the same scenario and seed.
> Across the final 10-seed experiment, adaptive control reduced mean waiting time in every tested
> scenario and maintained zero conflicting-green violations.

Screenshot fallback:

- `output/playwright/dashboard-benchmark-results.png`

## Segment 6: Generated Evidence

Open:

- `results/dissertation/results_summary.md`
- `results/dissertation/benchmark_summary.csv`
- `results/dissertation/failure_modes.csv`
- `results/dissertation/mean_wait.svg`
- `results/dissertation/max_queue.svg`
- `results/dissertation/completed.svg`

Say:

> The final result package is generated by script, so the figures and tables are reproducible. It
> writes row-level benchmark data, aggregate statistics, detector-fault results, SVG charts, and a
> markdown summary. The final results were regenerated after correcting the simulator so arrivals
> follow the configured demand rate and mean wait is measured from completed vehicles.

Command:

```powershell
.\.venv\Scripts\python.exe scripts\dissertation_results.py --duration 300 --step 0.5 --seeds 10 --output-dir results\dissertation
```

Key final result:

> Adaptive control reduced mean waiting time by about 8.33% to 43.11% across the benchmark
> scenarios, completed more vehicles than the fixed-time baseline, and recorded zero
> conflicting-green violations.

## Segment 7: Conclusion

Say:

> In conclusion, the project achieved the simulation-only objective. It implements a safe
> four-way traffic-light phase controller, compares fixed-time and adaptive timing, visualises
> live traffic, records experiment data, tests detector faults, and produces repeatable evaluation
> results. The main limitation is that it is a simplified simulator, so the results should be
> interpreted as evidence for this implementation rather than as a direct real-road prediction.

## Likely Questions and Short Answers

| Question | Answer |
|---|---|
| Why did you remove the hardware? | To focus on repeatable algorithm evaluation, safety testing, dashboard evidence, and quantitative results. Hardware can be added later, but it is not necessary to prove the controller logic. |
| What makes this engineering-related if similar systems already exist? | The project is a designed and tested software engineering system: it has requirements, controller logic, safety constraints, simulation, persistence, API, dashboard, benchmark scripts, generated evidence, and automated tests. It does not claim to invent adaptive traffic lights; it demonstrates and evaluates a complete implementation. |
| What is different from a basic traffic-light project? | It compares adaptive control against a fixed-time baseline using the same traffic traces, records quantitative metrics, tests detector faults, shows true queue versus detector demand, and produces repeatable result artifacts. |
| How are cars detected in a simulation-only system? | The simulator maintains true queues and exposes virtual detector demand to the controller. This replaces physical sensors for the approved simulation scope. |
| What about rain, darkness, glare, or poor visibility? | These are treated as possible causes of incorrect detector readings. The current project represents that through stuck-high and stuck-low fault profiles rather than physical camera or sensor modelling. |
| How is the adaptive controller different from fixed-time? | Fixed-time uses the same green duration every cycle. Adaptive control changes green duration using queue demand while staying within minimum and maximum green limits. |
| How do you know the comparison is fair? | Fixed and adaptive runs use the same scenario, duration, step size, and random seed, so they receive the same traffic arrival trace. |
| What prevents conflicting green lights? | The shared phase controller only creates safe movement-group states, and every state passes through `assert_no_conflicting_greens`. |
| What happens if a detector fails? | Faults alter the demand values seen by the controller, but they do not directly control the signal lights. The phase machine still enforces safe transitions. |
| What is your best result? | Adaptive control reduced mean wait in all five benchmark scenarios, with improvements from about 8.33% to 43.11%. |
| Did adaptive always improve every metric? | In the corrected 10-seed benchmark it improved mean wait, completed vehicles, and maximum queue in all five scenarios. Detector-fault runs still show that bad demand input can reduce performance. |
| Can this control a real road? | No. It is an academic simulation and not certified traffic-control equipment. Real deployment would require approved hardware, calibration, fail-safe monitoring, and legal authorisation. |

## Files to Show

| Purpose | File |
|---|---|
| Presentation deck | `traffic-light-demo-corrected.pptx` |
| Final assembled report | `docs/final-report/final-report.md` |
| Background | `docs/proposal/background-literature-review.md` |
| Requirements | `docs/proposal/requirements-specification.md` |
| Methodology | `docs/proposal/methodology-implementation.md` |
| Results | `docs/proposal/results-evaluation.md` |
| Live screenshot | `output/playwright/dashboard-live-simulation.png` |
| Fault screenshot | `output/playwright/dashboard-fault-mismatch.png` |
| Benchmark screenshot | `output/playwright/dashboard-benchmark-results.png` |
| Final result summary | `results/dissertation/results_summary.md` |

## Emergency Fallback Plan

If the live dashboard fails during the presentation:

1. Show the saved dashboard screenshots.
2. Show `results/dissertation/results_summary.md`.
3. Run `.\.venv\Scripts\python.exe -m pytest`.
4. Explain that the screenshots and CSVs were generated from the same dashboard and scripts.

This is enough to demonstrate the implementation and results even without a live browser run.
