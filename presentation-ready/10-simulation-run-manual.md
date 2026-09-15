# Simulation Run Manual

This manual explains how to start, run, and demonstrate the simulation dashboard for the
simulation-based adaptive smart traffic-light controller.

## Project Folder

Open PowerShell and go to the project folder:

```powershell
cd C:\Code\school\FinalYear\TrafficLight
```

Confirm you are in the right place:

```powershell
git branch --show-current
```

Expected branch:

```text
simulation-only
```

## First-Time Setup

If the virtual environment already exists, skip this section.

Create the virtual environment:

```powershell
py -3.11 -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the project:

```powershell
python -m pip install -e ".[dev,api]"
```

Run the tests:

```powershell
python -m pytest
```

Expected result:

```text
27 passed, 1 warning
```

## Normal Run

Start the dashboard server:

```powershell
.\.venv\Scripts\python.exe -m uvicorn trafficlight.api.app:app --host 127.0.0.1 --port 8000
```

Open this in a browser:

```text
http://127.0.0.1:8000/?v=countdowns-live
```

If port `8000` is busy, use port `8001`:

```powershell
.\.venv\Scripts\python.exe -m uvicorn trafficlight.api.app:app --host 127.0.0.1 --port 8001
```

Then open:

```text
http://127.0.0.1:8001/?v=countdowns-live
```

## Best Settings For Watching The Simulation

Use these settings when you want to see the cars move clearly:

| Control | Value |
|---|---|
| Controller | Adaptive |
| Scenario | NS-heavy |
| Fault profile | None |
| Duration | 120 |
| Step | 1 |
| Playback speed | Real time - 1x |
| Seed | 42 |

Then click `Run`.

For an even slower view, change:

| Control | Value |
|---|---|
| Playback speed | Slow detail - 0.5x |

## What To Watch On The Dashboard

The center road view shows:

- cars entering from each road;
- cars queueing before the stop line;
- cars crossing when their road is green;
- traffic lights for `N ROAD`, `S ROAD`, `E ROAD`, and `W ROAD`;
- highlighted green road corridor;
- direction labels `N`, `E`, `S`, and `W`.

The right panel shows:

- completed vehicles;
- mean waiting time;
- maximum queue;
- safety violations;
- detector mismatch;
- signal countdowns.

## Final Screenshot Evidence

Use these saved screenshots if the live demo is slow or the projector/browser fails:

| Screenshot | What it proves |
|---|---|
| ![Live simulation](screenshots/dashboard-live-simulation.png) | The dashboard shows moving vehicles, active roads, signal lamps, countdown timers, and live metrics. |
| ![Detector fault mismatch](screenshots/dashboard-fault-mismatch.png) | The system separates real simulated queues from faulty detector readings. |
| ![Benchmark results](screenshots/dashboard-benchmark-results.png) | The dashboard compares fixed-time and adaptive control using matching seeds and shows aggregate charts. |

## Signal Countdown Explanation

The `Signal Countdowns` panel shows the timer for each road:

| Field | Meaning |
|---|---|
| Big seconds value | Time left until that road changes state |
| `GREEN` | That road is currently allowed to move |
| `RED` | That road is currently stopped |
| `amber in ...` | The green road is about to move to amber |
| `green in ...` | A red road is waiting for its next green |
| `adaptive target ...` | Adaptive controller selected that green duration |
| Timer reset line | Phase changed and the countdown restarted |

Important defence point:

> The adaptive controller does not make unsafe jumps. It only changes green duration, then the
> phase machine still goes through amber and all-red clearance.

## Demo 1: Adaptive Heavy Demand

Use:

| Control | Value |
|---|---|
| Controller | Adaptive |
| Scenario | NS-heavy |
| Fault profile | None |
| Duration | 120 |
| Step | 1 |
| Playback speed | Real time - 1x |
| Seed | 42 |

Click `Run`.

What to say:

> This run shows the adaptive controller responding to heavier North/South traffic. The signal
> countdown shows the current green target, while the road view shows the queues and moving cars.

## Demo 2: Fixed-Time Baseline

Use:

| Control | Value |
|---|---|
| Controller | Fixed-time |
| Scenario | NS-heavy |
| Fault profile | None |
| Duration | 120 |
| Step | 1 |
| Playback speed | Real time - 1x |
| Seed | 42 |

Click `Run`.

What to say:

> This is the baseline. The fixed controller uses preset timing, so it cannot adjust green time
> based on demand.

## Demo 3: Detector Fault

Use:

| Control | Value |
|---|---|
| Controller | Adaptive |
| Scenario | NS-heavy |
| Fault profile | NS stuck high |
| Duration | 120 |
| Step | 1 |
| Playback speed | Real time - 1x |
| Seed | 42 |

Click `Run`.

What to say:

> This shows detector fault handling. The detector reading can differ from the real queue, but
> the detector cannot directly force unsafe green lights.

## Demo 4: Fixed vs Adaptive Comparison

Use:

| Control | Value |
|---|---|
| Scenario | NS-heavy |
| Duration | 300 |
| Step | 0.5 |
| Benchmark seeds | 5 or 10 |
| Seed | 1 |

Click `Compare Selected` to compare the selected scenario.

Click `Benchmark` to compare all scenarios.

What to say:

> The comparison uses the same scenario, duration, step size, and random seeds for fixed and
> adaptive controllers. This makes the comparison fair.

## Quick Demo Presets

The buttons under `Demo presets` fill the controls automatically:

| Button | Purpose |
|---|---|
| NS-heavy adaptive | Main adaptive demo |
| EW-heavy adaptive | Shows the same logic working on East/West demand |
| NS burst | Shows a temporary demand surge |
| Fixed baseline | Shows the baseline fixed-time controller |
| Detector fault | Shows detector mismatch behaviour |

## If The Page Looks Old

Open the cache-busted URL:

```text
http://127.0.0.1:8000/?v=countdowns-live
```

Or press:

```text
Ctrl + F5
```

## If The Server Is Already Running

If PowerShell says port `8000` is already in use, either open the existing dashboard or start on
port `8001`.

To check the process on port `8000`:

```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen
```

## If The Dashboard Fails During Presentation

Use the fallback evidence in:

```text
presentation-ready\screenshots
presentation-ready\evidence
```

Useful fallback files:

| File | Purpose |
|---|---|
| `screenshots/dashboard-live-simulation.png` | Shows the live simulation dashboard |
| `screenshots/dashboard-fault-mismatch.png` | Shows detector mismatch |
| `screenshots/dashboard-benchmark-results.png` | Shows benchmark results |
| `evidence/results_summary.md` | Summarises final benchmark evidence |
| `evidence/benchmark_summary.csv` | Aggregate benchmark data |
| `evidence/failure_modes.csv` | Detector-fault results |

## Short Explanation For A Presenter

> This project is a simulation-only adaptive smart traffic-light controller. It compares a
> fixed-time baseline with an adaptive controller under repeatable traffic scenarios. The
> dashboard shows cars, queues, signal lights, countdown timers, detector demand, benchmark
> results, and safety violations. The important engineering point is that adaptive logic changes
> green duration, but the shared phase machine still enforces amber and all-red safety clearance.
