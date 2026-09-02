const approaches = ["north", "east", "south", "west"];
const colours = ["red", "amber", "green"];
const history = [];
const maxHistory = 80;
const svgNamespace = "http://www.w3.org/2000/svg";

const state = {
  running: false,
  maxQueue: 0,
  socket: null,
};

const elements = {
  runButton: document.querySelector("#run-button"),
  benchmarkButton: document.querySelector("#benchmark-button"),
  status: document.querySelector("#connection-status"),
  controller: document.querySelector("#controller"),
  scenario: document.querySelector("#scenario"),
  duration: document.querySelector("#duration"),
  step: document.querySelector("#step"),
  seed: document.querySelector("#seed"),
  phase: document.querySelector("#phase"),
  phaseTime: document.querySelector("#phase-time"),
  reason: document.querySelector("#reason"),
  completed: document.querySelector("#completed"),
  meanWait: document.querySelector("#mean-wait"),
  maxQueue: document.querySelector("#max-queue"),
  violations: document.querySelector("#violations"),
  historyLine: document.querySelector("#history-line"),
  runsBody: document.querySelector("#runs-body"),
  benchmarkStatus: document.querySelector("#benchmark-status"),
  benchmarkBody: document.querySelector("#benchmark-body"),
  activeLayer: document.querySelector("#active-layer"),
  vehicleLayer: document.querySelector("#vehicle-layer"),
};

function setStatus(text) {
  elements.status.textContent = text;
}

function setBenchmarkRunning(running) {
  elements.benchmarkButton.disabled = running;
  elements.benchmarkButton.textContent = running ? "Benchmarking" : "Benchmark";
}

function setRunning(running) {
  state.running = running;
  elements.runButton.disabled = running;
  elements.runButton.textContent = running ? "Running" : "Run";
}

function params() {
  return new URLSearchParams({
    controller: elements.controller.value,
    scenario: elements.scenario.value,
    duration_s: elements.duration.value,
    step_s: elements.step.value,
    seed: elements.seed.value,
    persist: "true",
  });
}

function activateSignals(signals) {
  for (const approach of approaches) {
    for (const colour of colours) {
      const lamp = document.querySelector(`#${approach}-${colour}`);
      lamp.classList.toggle("is-active", signals[approach] === colour);
    }
  }
  renderActiveLanes(signals);
}

function updateQueues(queues) {
  let total = 0;
  for (const approach of approaches) {
    const value = queues[approach] ?? 0;
    total += value;
    state.maxQueue = Math.max(state.maxQueue, value);
    const meter = document.querySelector(`#queue-${approach}`);
    const label = document.querySelector(`#queue-${approach}-value`);
    meter.max = Math.max(80, state.maxQueue);
    meter.value = value;
    label.textContent = value;
  }
  elements.maxQueue.textContent = state.maxQueue;
  history.push(total);
  if (history.length > maxHistory) {
    history.shift();
  }
  drawHistory();
}

function svgElement(name, attributes = {}) {
  const element = document.createElementNS(svgNamespace, name);
  for (const [key, value] of Object.entries(attributes)) {
    element.setAttribute(key, value);
  }
  return element;
}

function carDimensions(direction) {
  const vertical = direction === "north" || direction === "south";
  return {
    width: vertical ? 16 : 26,
    height: vertical ? 26 : 16,
  };
}

function addVehicle(x, y, direction, mode) {
  const { width, height } = carDimensions(direction);
  const vehicle = svgElement("g", {
    transform: `translate(${x} ${y})`,
    class: `vehicle ${mode}`,
  });
  vehicle.append(
    svgElement("rect", {
      x: 0,
      y: 0,
      width,
      height,
      rx: 4,
      class: "body",
    })
  );
  vehicle.append(
    svgElement("rect", {
      x: width * 0.28,
      y: height * 0.25,
      width: width * 0.44,
      height: height * 0.5,
      rx: 2,
      class: "window",
    })
  );
  vehicle.append(svgElement("circle", { cx: width * 0.18, cy: height + 1, r: 2, class: "wheel" }));
  vehicle.append(svgElement("circle", { cx: width * 0.82, cy: height + 1, r: 2, class: "wheel" }));
  elements.vehicleLayer.append(vehicle);
  return vehicle;
}

function addQueuedVehicle(x, y, direction) {
  addVehicle(x, y, direction, "queued");
}

function addOverflowLabel(text, x, y) {
  const label = svgElement("text", {
    x,
    y,
    "text-anchor": "middle",
    class: "queue-overflow",
  });
  label.textContent = text;
  elements.vehicleLayer.append(label);
}

function addFlowVehicle(direction, laneOffset, delay) {
  const x = {
    north: 286 + laneOffset,
    south: 340 - laneOffset,
    east: 392,
    west: 224,
  }[direction];
  const y = {
    north: 224,
    south: 392,
    east: 286 + laneOffset,
    west: 340 - laneOffset,
  }[direction];
  const vehicle = addVehicle(x, y, direction, "flowing");

  const animate = svgElement("animateTransform", {
    attributeName: "transform",
    type: "translate",
    from: {
      north: `${x} 224`,
      south: `${x} 392`,
      east: `392 ${y}`,
      west: `224 ${y}`,
    }[direction],
    to: {
      north: `${x} 404`,
      south: `${x} 224`,
      east: `224 ${y}`,
      west: `392 ${y}`,
    }[direction],
    dur: "0.9s",
    begin: `${delay}s`,
    repeatCount: "indefinite",
  });
  vehicle.append(animate);
  elements.vehicleLayer.append(vehicle);
}

function renderActiveLanes(signals) {
  elements.activeLayer.innerHTML = "";
  const activeGroups = [
    signals.north === "green" || signals.south === "green" ? "northSouth" : null,
    signals.east === "green" || signals.west === "green" ? "eastWest" : null,
  ].filter(Boolean);
  for (const group of activeGroups) {
    if (group === "northSouth") {
      elements.activeLayer.append(svgElement("rect", { x: 260, y: 0, width: 120, height: 640, class: "active-lane" }));
    }
    if (group === "eastWest") {
      elements.activeLayer.append(svgElement("rect", { x: 0, y: 260, width: 640, height: 120, class: "active-lane" }));
    }
  }
}

function renderVehicles(queues, signals) {
  elements.vehicleLayer.innerHTML = "";
  const visibleLimit = 10;
  const configs = {
    north: { startX: 284, startY: 190, laneDx: 26, laneDy: 0, rowDx: 0, rowDy: -22 },
    south: { startX: 342, startY: 426, laneDx: -26, laneDy: 0, rowDx: 0, rowDy: 22 },
    east: { startX: 428, startY: 284, laneDx: 0, laneDy: 26, rowDx: 26, rowDy: 0 },
    west: { startX: 188, startY: 342, laneDx: 0, laneDy: -26, rowDx: -26, rowDy: 0 },
  };

  for (const approach of approaches) {
    const count = queues[approach] ?? 0;
    const visible = Math.min(count, visibleLimit);
    const config = configs[approach];
    for (let index = 0; index < visible; index += 1) {
      const lane = index % 2;
      const row = Math.floor(index / 2);
      addQueuedVehicle(
        config.startX + lane * config.laneDx + row * config.rowDx,
        config.startY + lane * config.laneDy + row * config.rowDy,
        approach
      );
    }
    if (count > visibleLimit) {
      const overflow = count - visibleLimit;
      addOverflowLabel(
        `+${overflow}`,
        {
          north: 320,
          south: 320,
          east: 540,
          west: 100,
        }[approach],
        {
          north: 72,
          south: 548,
          east: 320,
          west: 320,
        }[approach]
      );
    }
    if (signals[approach] === "green" && count > 0) {
      addFlowVehicle(approach, 0, 0);
      if (count > 3) {
        addFlowVehicle(approach, 28, 0.3);
      }
    }
  }
}

function drawHistory() {
  if (!history.length) {
    elements.historyLine.setAttribute("points", "");
    return;
  }
  const max = Math.max(1, ...history);
  const width = 552;
  const height = 116;
  const step = history.length > 1 ? width / (history.length - 1) : width;
  const points = history
    .map((value, index) => {
      const x = 32 + index * step;
      const y = 132 - (value / max) * height;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
  elements.historyLine.setAttribute("points", points);
}

function applyStep(message) {
  elements.phase.textContent = message.phase;
  elements.phaseTime.textContent = `${message.phase_elapsed_s.toFixed(1)}s`;
  elements.reason.textContent = message.reason;
  elements.completed.textContent = message.completed_vehicles;
  elements.meanWait.textContent =
    message.mean_wait_s === null ? "-" : `${message.mean_wait_s.toFixed(1)}s`;
  activateSignals(message.signals);
  updateQueues(message.queues);
  renderVehicles(message.queues, message.signals);
}

function applySummary(summary) {
  elements.completed.textContent = summary.completed;
  elements.meanWait.textContent = `${summary.mean_wait_s.toFixed(1)}s`;
  elements.maxQueue.textContent = summary.max_queue;
  elements.violations.textContent = summary.conflicting_green_violations;
}

function resetRunView() {
  state.maxQueue = 0;
  history.length = 0;
  elements.completed.textContent = "0";
  elements.meanWait.textContent = "-";
  elements.maxQueue.textContent = "0";
  elements.violations.textContent = "0";
  elements.phase.textContent = "all_red_to_ns";
  elements.phaseTime.textContent = "0.0s";
  elements.reason.textContent = "startup";
  drawHistory();
  renderVehicles({ north: 0, east: 0, south: 0, west: 0 }, {});
}

async function loadRuns() {
  const response = await fetch("/api/runs?limit=8");
  if (!response.ok) {
    return;
  }
  const runs = await response.json();
  elements.runsBody.innerHTML = "";
  for (const run of runs) {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${run.id}</td>
      <td>${run.scenario}</td>
      <td>${run.controller}</td>
      <td>${run.status}</td>
    `;
    elements.runsBody.append(row);
  }
}

function formatNumber(value, decimals = 1) {
  if (value === null || value === undefined) {
    return "-";
  }
  return Number(value).toFixed(decimals);
}

function formatImprovement(value) {
  if (value === null || value === undefined) {
    return "-";
  }
  const cssClass = value >= 0 ? "benchmark-positive" : "benchmark-negative";
  const prefix = value > 0 ? "+" : "";
  return `<span class="${cssClass}">${prefix}${value.toFixed(1)}%</span>`;
}

async function runBenchmark() {
  setBenchmarkRunning(true);
  elements.benchmarkStatus.textContent = "Running";
  elements.benchmarkBody.innerHTML = "";
  try {
    const response = await fetch("/api/benchmarks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        scenarios: ["balanced", "ns-heavy", "ew-heavy", "ns-burst", "alternating-peak"],
        seeds: [Number(elements.seed.value)],
        duration_s: Number(elements.duration.value),
        step_s: Number(elements.step.value),
      }),
    });
    if (!response.ok) {
      throw new Error(`Benchmark failed with status ${response.status}`);
    }
    const payload = await response.json();
    for (const row of payload.rows) {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${row.scenario}</td>
        <td>${row.seed}</td>
        <td>${row.controller}</td>
        <td>${row.completed}</td>
        <td>${formatNumber(row.mean_wait_s)}s</td>
        <td>${row.max_queue}</td>
        <td>${formatImprovement(row.mean_wait_improvement_pct)}</td>
        <td>${row.conflicting_green_violations}</td>
      `;
      elements.benchmarkBody.append(tr);
    }
    elements.benchmarkStatus.textContent = `${payload.rows.length} rows`;
  } catch (error) {
    elements.benchmarkStatus.textContent = "Failed";
  } finally {
    setBenchmarkRunning(false);
  }
}

function runSimulation() {
  if (state.running) {
    return;
  }
  resetRunView();
  setRunning(true);
  setStatus("Connecting");
  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  const socket = new WebSocket(`${protocol}://${window.location.host}/ws/simulation?${params()}`);
  state.socket = socket;

  socket.addEventListener("open", () => setStatus("Streaming"));
  socket.addEventListener("message", (event) => {
    const message = JSON.parse(event.data);
    if (message.type === "step") {
      applyStep(message);
    }
    if (message.type === "summary") {
      applySummary(message.summary);
      setStatus("Complete");
      loadRuns();
    }
  });
  socket.addEventListener("close", () => {
    setRunning(false);
    state.socket = null;
  });
  socket.addEventListener("error", () => {
    setStatus("Connection error");
    setRunning(false);
  });
}

elements.runButton.addEventListener("click", runSimulation);
elements.benchmarkButton.addEventListener("click", runBenchmark);
activateSignals({ north: "red", east: "red", south: "red", west: "red" });
renderVehicles({ north: 0, east: 0, south: 0, west: 0 }, {});
loadRuns();
