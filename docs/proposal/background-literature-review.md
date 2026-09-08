# Background and Literature Review Draft

This chapter places the simulation-only adaptive traffic-light project in context. It explains why
traffic-signal timing matters, how adaptive control differs from fixed-time operation, why
simulation is a suitable evaluation method for this project, and how the selected software tools
support the implementation.

## Traffic-Signal Control Problem

Urban intersections are natural congestion points because multiple traffic streams compete for the
same physical road space. A signal controller must allocate right of way between conflicting
movements while maintaining safety. Poor signal timing can increase delay, queue length, stop-start
movement, fuel use, and driver frustration. For a single four-arm intersection, the basic control
problem is to decide when North/South traffic should move, when East/West traffic should move, and
how long each movement should receive green time.

Conventional fixed-time traffic lights use a predetermined cycle. This is simple, predictable, and
easy to test, but it cannot react to changing demand. A fixed-time controller may give green time
to an empty approach while vehicles wait on another approach. This limitation motivates adaptive
signal control, where timing decisions respond to measured or estimated demand.

The Federal Highway Administration describes adaptive signal control technology as a way to adjust
signal timing to changing traffic patterns. This is the same broad idea used in this project:
traffic demand is measured in the simulation, and green duration changes according to queue
pressure rather than staying fixed for every cycle.[^fhwa-asct]

## Fixed-Time and Adaptive Control

Fixed-time signal control is an appropriate baseline because it represents a simple controller that
does not depend on live demand. In this project, the fixed-time baseline uses the same safety phase
sequence as the adaptive controller, but every green interval lasts for the configured fixed
duration. That makes the comparison fair: the safety logic is held constant while the timing policy
changes.

Adaptive control attempts to improve performance by reallocating green time towards movements with
higher demand. The project uses a deliberately explainable adaptive policy instead of a black-box
machine-learning model. The controller calculates queue demand on the active movement group and
the opposing movement group, then selects a target green duration between minimum and maximum
limits. This produces behaviour that can be inspected, tested, and defended in a final-year
project.

The main expected benefit is lower waiting time and lower queue length when demand is unequal or
changes during the run. The main risk is that over-serving a busy movement could starve another
movement. The project addresses this by enforcing a maximum green duration and by keeping the
phase transition sequence independent of the adaptive decision rule.

## Signal Timing and Safety

Traffic-signal timing is not only about choosing green time. Standard signal-control practice
distinguishes green, yellow or amber change, and red clearance intervals. FHWA signal-timing
guidance discusses minimum green, maximum green, yellow-change, and red-clearance parameters as
separate timing elements.[^fhwa-timing] This supports the project's design choice to model amber
and all-red clearance as explicit states rather than jumping directly from one green movement to
the opposing green movement.

The safety requirement in this project is strict: North/South green and East/West green must never
be active at the same time. The adaptive controller is therefore not allowed to set arbitrary lamp
states. It can only influence when a green phase ends. The shared phase controller still forces
the sequence:

```text
all-red -> green -> amber -> all-red -> opposing green
```

This separation matters because the project is evaluating adaptive timing, not replacing basic
traffic-signal safety logic. A controller that improves delay but allows conflicting greens would
be unacceptable. For this reason, the safety metric is reported separately from performance
metrics, and the target is zero conflicting-green violations.

## Simulation as an Evaluation Method

This project moved away from physical hardware and now uses a total software simulation. That is a
reasonable scope choice for a final-year project because it allows repeatable, measurable
experiments without waiting for Raspberry Pi hardware, cameras, sensors, or a physical road model.
Simulation also avoids the safety and legal problems of experimenting with real public-road
signals.

The purpose of the simulator is not to reproduce every detail of real traffic. Instead, it creates
a controlled environment where the fixed-time and adaptive controllers can be exposed to identical
traffic demand. Each simulation run uses a scenario, duration, step size, and random seed. Running
the fixed and adaptive controllers with the same seed allows direct comparison under the same
arrival trace.

The simulation records:

- vehicle arrivals
- completed vehicles
- waiting time
- maximum queue length
- signal phase transitions
- controller-visible detector demand
- conflicting-green violations

Traffic simulation is also a recognised approach in transport research. SUMO, for example, is an
open-source traffic simulation package whose documentation describes traffic-light modelling as a
way to replicate existing signals and simulate traffic-light algorithms for research.[^sumo-tl]
This project does not use SUMO as its primary simulator because a lightweight custom simulator is
easier to test and explain, but SUMO remains a possible future validation tool.

## Demand, Delay, Queue, and Throughput Metrics

The project evaluates adaptive control using metrics commonly associated with intersection
performance:

| Metric | Meaning in this project |
|---|---|
| Completed vehicles | Vehicles discharged through the intersection during the run |
| Throughput | Completed vehicles per minute |
| Mean wait | Total accumulated queue waiting time divided by completed vehicles |
| Maximum queue | Largest queue observed on any approach during the run |
| Conflicting-green violations | Count of unsafe signal states observed by the safety check |

Mean wait is the main performance metric because the controller's purpose is to reduce time spent
waiting at the intersection. Maximum queue is also important because long queues can block upstream
traffic even if average waiting time improves. Completed vehicles gives a throughput measure and
helps detect whether a controller improves delay by simply serving fewer vehicles.

The dissertation results should report both average performance and spread. This project therefore
uses multiple seeds and reports standard deviation plus an approximate 95% confidence interval for
aggregate benchmark metrics. Reporting spread is more defensible than selecting a single favourable
run because it shows how consistent the observed improvement is across random traffic inputs.

## Detector Faults and Robustness

Adaptive signal control depends on detector input. If detectors are wrong, the controller may make
poor timing decisions even when the phase logic remains safe. This project therefore includes
simulated detector faults to separate performance robustness from signal safety.

The implemented fault profiles represent common failure patterns:

- stuck-high demand, where a detector always reports heavy demand
- stuck-low demand, where a detector reports no demand despite real queues
- mid-run all-low failure, where all demand readings drop to zero halfway through the experiment

These tests are important because adaptive control should not be evaluated only under ideal
detector conditions. In the current implementation, detector faults can degrade wait time,
throughput, or queue length, but they cannot directly produce conflicting green indications because
all lamp output still passes through the shared safe phase sequence.

## Software Architecture Context

The implementation follows a layered architecture. The domain layer contains the controller,
signal states, timing configuration, and safety checks. The simulation layer provides queue
dynamics, scenarios, benchmark execution, fault injection, and reporting. The storage layer records
run data in SQLite. The interface layer provides the command line program, FastAPI API, WebSocket
stream, and browser dashboard.

FastAPI is suitable for this project because it supports typed HTTP APIs, JSON request/response
handling, and automatic OpenAPI documentation for HTTP endpoints.[^fastapi-docs] FastAPI also
supports WebSockets, which the dashboard uses for live simulation updates.[^fastapi-ws]

SQLite is suitable because the project is a local single-application simulator and does not need a
separate database server. SQLite's write-ahead logging documentation explains WAL as a journaling
mode using a separate WAL file while a connection is open.[^sqlite-wal] This kind of embedded
database design is practical for logging simulation runs, signal events, detector samples, and
traffic metrics.

pytest is used for automated verification. Its parametrization support allows the same test logic
to be applied across different scenarios and inputs.[^pytest-parametrize] This matters for safety
testing because the project needs repeated assurance that no scenario or timing condition creates
conflicting green states.

## Gap Addressed by This Project

The project does not claim to build a certified real-world traffic controller. Its contribution is
more focused: it implements a transparent adaptive controller, evaluates it against a fixed-time
baseline under repeatable simulation scenarios, records quantitative evidence, and verifies that
the phase machine maintains zero conflicting-green violations.

The project therefore addresses a practical final-year engineering gap between a simple traffic
light demonstration and a full transport-engineering control system. It is more rigorous than only
flashing LEDs because it includes benchmark data, safety tests, detector-fault experiments, and a
dashboard. At the same time, it remains achievable because it avoids the complexity of real road
deployment, camera calibration, hardware procurement, and certified signal equipment.

## Summary

The literature and technical background support the simulation-only direction. Fixed-time control
is easy to implement but cannot react to demand. Adaptive signal control aims to improve timing
under changing traffic conditions. Safe signal control requires explicit amber and all-red
clearance states. Simulation provides a repeatable way to compare fixed and adaptive controllers
under identical traffic inputs. The selected Python, FastAPI, SQLite, pytest, and browser
dashboard stack supports a complete software evaluation without requiring physical devices.

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
