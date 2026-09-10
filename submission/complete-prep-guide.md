# Complete Project Preparation Guide

This single guide explains what the project is, how it works, what was built, the final results,
how to demonstrate it, and how to answer likely examiner questions.

## Project Title

**Design and Evaluation of a Simulation-Based Adaptive Smart Traffic-Light Controller**

Short title: **Simulation-Based Adaptive Smart Traffic-Light Controller**

## Project Details

| Item | Detail |
|---|---|
| Institution | GHANA COMMUNICATION TECHNOLOGY UNIVERSITY (GCTU) |
| Faculty | FACULTY OF ENGINEERING |
| Department | DEPARTMENT OF COMPUTER ENGINEERING |
| Student 1 | HENYO THEOPHILUS - ID 4121230031 |
| Student 2 | DJAGNI JERRY KODJO - ID 4121230036 |
| Supervisor | DR. PHILLIP KISEMBE |

## One-Minute Summary

This project implements a software simulation of a four-way smart traffic-light controller. It
compares a fixed-time controller against an adaptive controller that changes green duration based
on simulated traffic demand. The system includes a live browser dashboard, detector-fault
simulation, SQLite logging, benchmark scripts, generated CSV/SVG result artifacts, a presentation
deck, and automated tests.

The final project is simulation-only. It does not use Raspberry Pi hardware, GPIO wiring, cameras,
or real road equipment. The engineering contribution is the complete design, implementation,
testing, visualisation, and evaluation of the controller under repeatable simulated conditions.

## Main Problem

Fixed-time traffic lights use preset green durations even when traffic demand changes. This can
increase waiting time and queue length, especially when one road is much busier than the other.
The project investigates whether a demand-responsive adaptive controller can reduce waiting time
and queues while still maintaining safe traffic-light phases.

## What Was Built

| Area | What it does |
|---|---|
| Traffic-light controller | Controls North/South and East/West signal phases |
| Fixed-time baseline | Uses the same green duration every cycle |
| Adaptive controller | Changes green time based on detector demand |
| Simulator | Generates vehicle arrivals, queues, departures, waiting time, and completed vehicles |
| Virtual detectors | Provide simulated demand readings to the controller |
| Detector faults | Simulate wrong readings such as stuck-high and stuck-low sensors |
| Dashboard | Shows live vehicles, queues, lights, metrics, detector readings, and benchmark results |
| API/WebSocket | Connects the simulator to the dashboard |
| SQLite logging | Stores runs, signal events, detector samples, and traffic metrics |
| Benchmark scripts | Compare fixed and adaptive controllers over repeated seeds |
| Report artifacts | Generate CSVs, charts, screenshots, Markdown, DOCX, and PDF outputs |
| Tests | Verify controller safety, simulation behaviour, API, storage, benchmark, and reporting |

## How The Controller Works

The system models a four-way intersection with four approaches:

- North
- East
- South
- West

The movements are grouped into two non-conflicting groups:

- North/South
- East/West

The safe phase sequence is:

```text
all-red -> NS green -> NS amber -> all-red -> EW green -> EW amber -> all-red
```

The fixed-time controller always uses the same green duration. The adaptive controller uses
virtual detector demand to choose a green duration between minimum and maximum limits.

Default timing:

| Timing item | Value |
|---|---:|
| Minimum green | 8 seconds |
| Fixed green baseline | 20 seconds |
| Maximum green | 45 seconds |
| Amber | 3 seconds |
| All-red clearance | 2 seconds |

Important safety point: adaptive logic only changes how long green lasts. It cannot skip amber,
skip all-red, or directly force unsafe lights.

## How Cars Are Detected In Simulation

Because this project is simulation-only, cars are not detected by physical sensors or cameras.
The simulator keeps the true queue length for each approach and exposes virtual detector readings
to the controller.

This means:

- true queues are the real simulated vehicle queues;
- detector demand is what the controller sees;
- detector faults can make those two values different;
- the dashboard shows both, so the examiner can see when detector readings are wrong.

## Rain, Darkness, Glare, Dirt, And Other Real-World Conditions

The project does not simulate weather visually. Instead, conditions like rain, darkness, glare,
dirt, poor visibility, or sensor damage are treated as possible causes of bad detector readings.

The implemented fault profiles are:

| Fault profile | Meaning |
|---|---|
| `none` | Normal detector readings |
| `ns-stuck-high` | North/South detector demand is forced high |
| `ew-stuck-low` | East/West detector demand is forced to zero |
| `all-stuck-low-midrun` | All detector readings become zero halfway through the run |

This is enough for the approved scope because the project evaluates traffic-control logic, not
computer vision or physical camera detection.

## Why This Is Engineering-Related

The project is engineering-related because it turns a real traffic-control problem into a
testable software system with:

- requirements;
- controller design;
- safety constraints;
- adaptive decision logic;
- simulator design;
- detector-fault modelling;
- persistent logging;
- API and dashboard interface;
- benchmark automation;
- generated evidence;
- automated regression tests;
- documented limitations.

The project does not claim that adaptive traffic lights are a new invention. The contribution is
the implemented and evaluated system.

## What Makes This Different From A Basic Traffic-Light Project

A basic traffic-light project usually just changes LEDs on a timer. This project goes further by:

- comparing fixed-time and adaptive control;
- using identical random seeds for fair comparison;
- measuring waiting time, queue length, completed vehicles, and safety violations;
- showing visible vehicles in a live dashboard;
- separating true queue values from detector demand;
- testing detector faults;
- exporting CSVs and charts;
- providing a repeatable benchmark workflow;
- verifying safety with automated tests.

## Final Experiment Setup

| Item | Value |
|---|---|
| Duration per run | 300 seconds |
| Simulation step | 0.5 seconds |
| Seeds | 1 to 10 |
| Controllers | Fixed-time and adaptive |
| Scenarios | Balanced, NS-heavy, EW-heavy, NS-burst, alternating peak |
| Main metrics | Mean wait, max queue, completed vehicles, safety violations |

Each fixed/adaptive comparison uses the same scenario, duration, step size, and random seed. This
keeps the traffic arrival trace the same for both controllers.

## Final Results

Across the final 10-seed benchmark:

- adaptive control reduced mean waiting time in all five scenarios;
- adaptive control completed more vehicles in all five scenarios;
- adaptive control reduced maximum queue length in all five scenarios;
- the system recorded zero conflicting-green safety violations.

| Scenario | Fixed mean wait | Adaptive mean wait | Wait improvement | Completed change | Safety violations |
|---|---:|---:|---:|---:|---:|
| Balanced | 23.91 s | 21.89 s | +8.33% | +1.90 | 0 |
| NS-heavy | 43.93 s | 29.51 s | +32.54% | +41.60 | 0 |
| EW-heavy | 50.15 s | 28.48 s | +43.11% | +42.70 | 0 |
| NS-burst | 44.10 s | 37.82 s | +14.46% | +36.50 | 0 |
| Alternating peak | 54.58 s | 38.09 s | +30.76% | +23.50 | 0 |

Best result: the EW-heavy scenario had the largest mean-wait improvement, about **43.11%**.

## Detector-Fault Results

| Fault profile | Mean completed | Mean wait | Mean max queue | Safety violations |
|---|---:|---:|---:|---:|
| none | 196.50 | 29.51 s | 22.90 | 0 |
| ns-stuck-high | 198.40 | 26.52 s | 17.40 | 0 |
| ew-stuck-low | 197.50 | 24.29 s | 17.30 | 0 |
| all-stuck-low-midrun | 160.60 | 34.18 s | 41.00 | 0 |

The severe all-stuck-low-midrun fault reduced performance, but it still did not create unsafe
conflicting green lights. This shows the difference between performance robustness and signal
safety.

## Demo Plan

Target length: 6 to 8 minutes.

| Time | Segment |
|---:|---|
| 0:00-0:45 | Introduce problem and simulation-only scope |
| 0:45-1:45 | Explain controller and safety design |
| 1:45-3:00 | Show live dashboard simulation |
| 3:00-4:00 | Show detector-fault behaviour |
| 4:00-5:30 | Show benchmark results and charts |
| 5:30-6:30 | Show tests and generated artifacts |
| 6:30-8:00 | Conclude and answer questions |

## Demo Commands

Open the project folder:

```powershell
cd C:\Code\school\FinalYear\TrafficLight
```

Check branch:

```powershell
git branch --show-current
```

Expected:

```text
simulation-only
```

Run tests:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Expected:

```text
24 passed, 1 warning
```

Start dashboard:

```powershell
.\.venv\Scripts\python.exe -m uvicorn trafficlight.api.app:app --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000/
```

If port 8000 is busy, use port 8001.

## Dashboard Demo Settings

Live adaptive run:

| Control | Value |
|---|---|
| Controller | Adaptive |
| Scenario | NS-heavy |
| Fault profile | None |
| Duration | 120 |
| Step | 1 |
| Seed | 42 |

Detector-fault run:

| Control | Value |
|---|---|
| Controller | Adaptive |
| Scenario | NS-heavy |
| Fault profile | NS stuck high |
| Duration | 120 |
| Step | 1 |
| Seed | 42 |

Benchmark run:

| Control | Value |
|---|---|
| Duration | 300 |
| Step | 0.5 |
| Seed | 1 |
| Benchmark seeds | 10 |

## What To Say During The Demo

Opening:

> My project is a simulation-based adaptive smart traffic-light controller for a four-way
> intersection. It compares adaptive demand-based timing with a fixed-time baseline using
> repeatable experiments.

Safety:

> The adaptive controller only changes the green duration. It cannot bypass amber or all-red
> clearance, so safety is enforced by the shared phase machine.

Dashboard:

> The dashboard is connected to the simulator through a WebSocket. Each step sends the phase,
> signal colours, queue lengths, detector demand, completed vehicles, and waiting-time metrics.

Faults:

> Detector faults change what the controller thinks the demand is, but they do not directly set
> the lights. This separates performance from safety.

Results:

> Adaptive control reduced mean wait by about 8.33% to 43.11% across the benchmark scenarios,
> completed more vehicles, reduced maximum queues, and recorded zero conflicting-green
> violations.

Conclusion:

> The project meets the simulation-only objective. It is not a certified real-road system, but it
> is a complete, tested, repeatable engineering implementation.

## Likely Examiner Questions

| Question | Short answer |
|---|---|
| Why no physical hardware? | The approved scope is simulation-only. This allows repeatable testing, measurable evaluation, and stronger evidence than simply blinking physical LEDs. |
| How is this engineering? | It includes requirements, controller logic, safety rules, simulation, fault modelling, logging, API, dashboard, benchmarks, report exports, and tests. |
| What is new if adaptive traffic lights already exist? | The novelty is not inventing adaptive signals; it is building and evaluating a complete implementation with fair fixed/adaptive comparison, detector faults, dashboard evidence, and safety testing. |
| How are cars detected? | The simulator creates true queues and virtual detector readings. The controller uses the virtual detector readings. |
| What about rain or darkness? | They are represented as detector-error causes through stuck-high and stuck-low fault profiles, not as visual weather simulation. |
| Why not camera detection? | Camera detection would be a separate computer-vision project. This project focuses on traffic-control logic and repeatable evaluation. |
| How do you know the comparison is fair? | Fixed and adaptive runs use the same scenario, duration, step size, and seed. |
| What prevents unsafe green lights? | The shared phase controller and safety check reject North/South and East/West green at the same time. |
| What happens if a detector fails? | Performance may degrade, but safety remains because detector readings cannot directly command the lights. |
| Can it control a real road? | No. Real deployment would need certified hardware, calibrated data, field testing, fail-safe design, and legal approval. |
| What are the limitations? | No pedestrians, turning movements, emergency vehicles, lane changes, real detector noise distributions, calibrated field data, or certified hardware. |
| What future work should be done? | SUMO validation, calibrated traffic data, richer detector-noise models, pedestrian/emergency phases, turning movement support, and optional hardware adapters. |

## Important Files In This Folder

| File/folder | Why it matters |
|---|---|
| `01-presentation-deck.pptx` | Main defence slides |
| `02-final-report-gctu-structure.pdf` | Report to read first |
| `02-final-report-gctu-structure.docx` | Editable Word report |
| `03-demonstration-script.md` | Step-by-step demo script |
| `04-demo-rehearsal-result.md` | Evidence that the demo path was tested |
| `05-final-submission-checklist.md` | Final submission checks |
| `07-final-details-needed.md` | Personal/institution details still needed |
| `08-defence-qa-cheat-sheet.md` | Short examiner Q&A |
| `screenshots/` | Fallback screenshots if live demo fails |
| `evidence/` | CSVs, charts, and result summary |

## Evidence Files To Know

| Evidence | Purpose |
|---|---|
| `evidence/results_summary.md` | Final result summary |
| `evidence/benchmark_rows.csv` | Row-level fixed/adaptive benchmark data |
| `evidence/benchmark_summary.csv` | Aggregate benchmark statistics |
| `evidence/failure_modes.csv` | Detector-fault experiment results |
| `evidence/mean_wait.svg` | Mean waiting-time chart |
| `evidence/max_queue.svg` | Maximum queue chart |
| `evidence/completed.svg` | Completed vehicles chart |
| `screenshots/dashboard-live-simulation.png` | Live simulation screenshot |
| `screenshots/dashboard-fault-mismatch.png` | Detector fault screenshot |
| `screenshots/dashboard-benchmark-results.png` | Benchmark dashboard screenshot |

## Emergency Fallback

If the live dashboard fails during the defence:

1. Show `screenshots/dashboard-live-simulation.png`.
2. Show `screenshots/dashboard-fault-mismatch.png`.
3. Show `screenshots/dashboard-benchmark-results.png`.
4. Open `evidence/results_summary.md`.
5. Run `.\.venv\Scripts\python.exe -m pytest`.
6. Explain that the screenshots and CSVs were generated from the same simulator and dashboard.

## Final Details Status

The student and supervisor details have been added:

- HENYO THEOPHILUS - ID 4121230031
- DJAGNI JERRY KODJO - ID 4121230036
- DR. PHILLIP KISEMBE

Still confirm:

- exact programme/faculty wording;
- citation style required by the department;
- whether to submit DOCX, PDF, printed copy, repository, or all.

## Strong Final Defence Statement

This project is engineering-focused because it designs and tests a traffic-control system with
safety constraints, adaptive timing, repeatable simulation, detector-fault modelling, measured
performance, and generated evidence. It is not a real-road deployment, but it is a complete and
defensible simulation-based implementation.
