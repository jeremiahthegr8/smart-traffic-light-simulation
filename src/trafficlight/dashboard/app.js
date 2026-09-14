const approaches = ["north", "east", "south", "west"];
const colours = ["red", "amber", "green"];
const benchmarkScenarios = ["balanced", "ns-heavy", "ew-heavy", "ns-burst", "alternating-peak"];
const history = [];
const maxHistory = 80;
const svgNamespace = "http://www.w3.org/2000/svg";
const presetConfig = {
  "adaptive-ns": {
    controller: "adaptive",
    scenario: "ns-heavy",
    faultProfile: "none",
    duration: 120,
    step: 1,
    seed: 42,
  },
  "adaptive-ew": {
    controller: "adaptive",
    scenario: "ew-heavy",
    faultProfile: "none",
    duration: 120,
    step: 1,
    seed: 42,
  },
  burst: {
    controller: "adaptive",
    scenario: "ns-burst",
    faultProfile: "none",
    duration: 180,
    step: 1,
    seed: 42,
  },
  fixed: {
    controller: "fixed",
    scenario: "ns-heavy",
    faultProfile: "none",
    duration: 120,
    step: 1,
    seed: 42,
  },
  fault: {
    controller: "adaptive",
    scenario: "ns-heavy",
    faultProfile: "ns-stuck-high",
    duration: 120,
    step: 1,
    seed: 42,
  },
};
const demoNotes = {
  balanced: {
    title: "Balanced traffic",
    description: "Shows the controller under even demand, where adaptive control should behave conservatively and still preserve safety.",
  },
  "ns-heavy": {
    title: "North/South heavy demand",
    description: "Shows adaptive timing giving more service to the busier North/South movement while the phase machine prevents conflicting greens.",
  },
  "ew-heavy": {
    title: "East/West heavy demand",
    description: "Shows that the same adaptive logic works when the heavier flow is on the East/West road instead of North/South.",
  },
  "ns-burst": {
    title: "Temporary demand burst",
    description: "Shows a changing-demand case where the queue grows during a burst and the controller responds without changing safety rules.",
  },
  "alternating-peak": {
    title: "Alternating peak demand",
    description: "Shows a demand shift over time, useful for explaining why fixed-time control struggles with changing traffic patterns.",
  },
};

const state = {
  running: false,
  maxQueue: 0,
  socket: null,
  scenarios: {},
  faultProfiles: {},
  lastSummary: null,
  lastBenchmarkRows: [],
  lastBenchmarkAggregates: [],
};

const elements = {
  runButton: document.querySelector("#run-button"),
  stopButton: document.querySelector("#stop-button"),
  resetButton: document.querySelector("#reset-button"),
  benchmarkButton: document.querySelector("#benchmark-button"),
  compareButton: document.querySelector("#compare-button"),
  tourButton: document.querySelector("#tour-button"),
  copyEvidenceButton: document.querySelector("#copy-evidence-button"),
  presetButtons: document.querySelectorAll(".preset-button"),
  status: document.querySelector("#connection-status"),
  controller: document.querySelector("#controller"),
  scenario: document.querySelector("#scenario"),
  customEnabled: document.querySelector("#custom-enabled"),
  customNorth: document.querySelector("#custom-north"),
  customEast: document.querySelector("#custom-east"),
  customSouth: document.querySelector("#custom-south"),
  customWest: document.querySelector("#custom-west"),
  faultProfile: document.querySelector("#fault-profile"),
  duration: document.querySelector("#duration"),
  step: document.querySelector("#step"),
  seed: document.querySelector("#seed"),
  benchmarkSeeds: document.querySelector("#benchmark-seeds"),
  phase: document.querySelector("#phase"),
  phaseTime: document.querySelector("#phase-time"),
  reason: document.querySelector("#reason"),
  completed: document.querySelector("#completed"),
  meanWait: document.querySelector("#mean-wait"),
  maxQueue: document.querySelector("#max-queue"),
  violations: document.querySelector("#violations"),
  faultActive: document.querySelector("#fault-active"),
  busiestApproach: document.querySelector("#busiest-approach"),
  detectorMismatch: document.querySelector("#detector-mismatch"),
  historyLine: document.querySelector("#history-line"),
  runsBody: document.querySelector("#runs-body"),
  benchmarkStatus: document.querySelector("#benchmark-status"),
  benchmarkBody: document.querySelector("#benchmark-body"),
  benchmarkWaitChart: document.querySelector("#benchmark-wait-chart"),
  benchmarkQueueChart: document.querySelector("#benchmark-queue-chart"),
  activeLayer: document.querySelector("#active-layer"),
  vehicleLayer: document.querySelector("#vehicle-layer"),
  demoTitle: document.querySelector("#demo-title"),
  demoDescription: document.querySelector("#demo-description"),
  scenarioDescription: document.querySelector("#scenario-description"),
  scenarioRates: document.querySelector("#scenario-rates"),
  scenarioWindows: document.querySelector("#scenario-windows"),
  evidenceSafety: document.querySelector("#evidence-safety"),
  evidenceWait: document.querySelector("#evidence-wait"),
  evidenceFault: document.querySelector("#evidence-fault"),
  faultDescription: document.querySelector("#fault-description"),
  examinerSummary: document.querySelector("#examiner-summary"),
};

function setStatus(text) {
  elements.status.textContent = text;
}

function setBenchmarkRunning(running) {
  elements.benchmarkButton.disabled = running;
  elements.compareButton.disabled = running;
  elements.tourButton.disabled = running;
  elements.benchmarkButton.textContent = running ? "Benchmarking" : "Benchmark";
  elements.compareButton.textContent = running ? "Comparing" : "Compare Selected";
}

function setRunning(running) {
  state.running = running;
  elements.runButton.disabled = running;
  elements.stopButton.disabled = !running;
  elements.tourButton.disabled = running;
  elements.runButton.textContent = running ? "Running" : "Run";
}

function params(persist = "true") {
  const values = new URLSearchParams({
    controller: elements.controller.value,
    scenario: elements.customEnabled.checked ? "custom-dashboard" : elements.scenario.value,
    fault_profile: elements.faultProfile.value,
    duration_s: elements.duration.value,
    step_s: elements.step.value,
    seed: elements.seed.value,
    persist,
  });
  if (elements.customEnabled.checked) {
    const custom = customArrivals();
    values.set("custom_north", custom.north);
    values.set("custom_east", custom.east);
    values.set("custom_south", custom.south);
    values.set("custom_west", custom.west);
  }
  return values;
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

function titleCase(value) {
  return `${value.charAt(0).toUpperCase()}${value.slice(1)}`;
}

function updateQueues(queues) {
  let total = 0;
  let busiest = { approach: "-", value: 0 };
  for (const approach of approaches) {
    const value = queues[approach] ?? 0;
    total += value;
    if (value > busiest.value) {
      busiest = { approach, value };
    }
    state.maxQueue = Math.max(state.maxQueue, value);
    const meter = document.querySelector(`#queue-${approach}`);
    const label = document.querySelector(`#queue-${approach}-value`);
    meter.max = Math.max(80, state.maxQueue);
    meter.value = value;
    label.textContent = value;
  }
  elements.busiestApproach.textContent =
    busiest.approach === "-" ? "-" : `${titleCase(busiest.approach)} (${busiest.value})`;
  elements.maxQueue.textContent = state.maxQueue;
  history.push(total);
  if (history.length > maxHistory) {
    history.shift();
  }
  drawHistory();
}

function updateDetectorDemand(demand) {
  for (const approach of approaches) {
    const label = document.querySelector(`#demand-${approach}-value`);
    label.textContent = Math.round(demand[approach] ?? 0);
    label.classList.toggle("benchmark-negative", Math.round(demand[approach] ?? 0) !== Number(document.querySelector(`#queue-${approach}-value`).textContent));
  }
}

function updateDetectorMismatch(queues, demand) {
  const mismatch = approaches.reduce((sum, approach) => {
    const queueValue = queues[approach] ?? 0;
    const demandValue = Math.round(demand[approach] ?? 0);
    return sum + Math.abs(queueValue - demandValue);
  }, 0);
  elements.detectorMismatch.textContent = mismatch;
  elements.detectorMismatch.classList.toggle("benchmark-negative", mismatch > 0);
  elements.detectorMismatch.classList.toggle("benchmark-positive", mismatch === 0);
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
  elements.faultActive.textContent = elements.faultProfile.value;
  elements.meanWait.textContent =
    message.mean_wait_s === null ? "-" : `${message.mean_wait_s.toFixed(1)}s`;
  activateSignals(message.signals);
  updateQueues(message.queues);
  updateDetectorDemand(message.demand);
  updateDetectorMismatch(message.queues, message.demand);
  renderVehicles(message.queues, message.signals);
}

function updateDemoNote() {
  if (elements.customEnabled.checked) {
    elements.demoTitle.textContent =
      `${elements.controller.value === "adaptive" ? "Adaptive" : "Fixed-time"}: Custom arrivals`;
    elements.demoDescription.textContent =
      "Uses your manual arrival rates to stress-test the controller under a what-if traffic pattern.";
    updateScenarioDetails();
    updateFaultDetails();
    return;
  }
  const note = demoNotes[elements.scenario.value] ?? demoNotes["ns-heavy"];
  const controller = elements.controller.value === "adaptive" ? "Adaptive" : "Fixed-time";
  const fault =
    elements.faultProfile.value === "none"
      ? ""
      : ` Fault profile: ${elements.faultProfile.value.replaceAll("-", " ")}.`;
  elements.demoTitle.textContent = `${controller}: ${note.title}`;
  elements.demoDescription.textContent = `${note.description}${fault}`;
  updateScenarioDetails();
  updateFaultDetails();
}

function customArrivals() {
  return {
    north: Math.max(0, Number(elements.customNorth.value || 0)),
    east: Math.max(0, Number(elements.customEast.value || 0)),
    south: Math.max(0, Number(elements.customSouth.value || 0)),
    west: Math.max(0, Number(elements.customWest.value || 0)),
  };
}

function updateScenarioDetails() {
  if (elements.customEnabled.checked) {
    const arrivals = customArrivals();
    elements.scenarioDescription.textContent =
      "Custom dashboard scenario using manually selected vehicle arrival rates per minute.";
    elements.scenarioRates.innerHTML = "";
    for (const approach of approaches) {
      const item = document.createElement("div");
      item.innerHTML = `<span>${approach}</span><strong>${arrivals[approach]}/min</strong>`;
      elements.scenarioRates.append(item);
    }
    elements.scenarioWindows.textContent = "No timed demand windows in custom mode.";
    return;
  }
  const scenario = state.scenarios[elements.scenario.value];
  if (!scenario) {
    elements.scenarioDescription.textContent = "Scenario details are loading.";
    elements.scenarioRates.innerHTML = "";
    elements.scenarioWindows.textContent = "";
    return;
  }
  elements.scenarioDescription.textContent = scenario.description;
  elements.scenarioRates.innerHTML = "";
  for (const approach of approaches) {
    const item = document.createElement("div");
    item.innerHTML = `<span>${approach}</span><strong>${scenario.arrivals_per_minute[approach] ?? 0}/min</strong>`;
    elements.scenarioRates.append(item);
  }
  if (!scenario.demand_windows.length) {
    elements.scenarioWindows.textContent = "No timed demand windows.";
    return;
  }
  elements.scenarioWindows.textContent = scenario.demand_windows
    .map((window) => `${window.start_s}s-${window.end_s}s demand changes`)
    .join("; ");
}

function updateFaultDetails() {
  const faults = state.faultProfiles[elements.faultProfile.value] ?? [];
  if (!faults.length) {
    elements.faultDescription.textContent = "No detector fault is selected.";
    elements.evidenceFault.textContent = "None selected";
    elements.evidenceFault.className = "";
    return;
  }
  elements.faultDescription.textContent = faults
    .map((fault) => `${fault.approaches.join(", ")} ${fault.mode.replace("_", " ")} from ${fault.start_s}s to ${fault.end_s}s`)
    .join("; ");
  elements.evidenceFault.textContent = elements.faultProfile.value.replaceAll("-", " ");
  elements.evidenceFault.className = "benchmark-negative";
}

function activeScenarioName() {
  return elements.customEnabled.checked ? "custom-dashboard" : elements.scenario.value;
}

function activeScenarioLabel() {
  if (!elements.customEnabled.checked) {
    return elements.scenario.value;
  }
  return `custom arrivals (${Object.entries(customArrivals())
    .map(([key, value]) => `${key} ${value}/min`)
    .join(", ")})`;
}

function setExaminerSummary(text) {
  elements.examinerSummary.textContent = text;
}

function signedNumber(value, decimals = 1) {
  if (value === null || value === undefined) {
    return "-";
  }
  const number = Number(value);
  return `${number >= 0 ? "+" : ""}${number.toFixed(decimals)}`;
}

function updateExaminerSummaryFromLiveRun(summary) {
  const controller = summary.controller === "adaptive" ? "Adaptive" : "Fixed-time";
  setExaminerSummary(
    `${controller} control on ${activeScenarioLabel()} completed ${summary.completed} vehicles with ` +
      `${summary.mean_wait_s.toFixed(1)}s mean wait, maximum queue ${summary.max_queue}, and ` +
      `${summary.conflicting_green_violations} conflicting-green safety violations.`
  );
}

function updateExaminerSummaryFromComparison() {
  const aggregate = selectedAdaptiveAggregate();
  if (!aggregate || aggregate.mean_wait_improvement_pct === null || aggregate.mean_wait_improvement_pct === undefined) {
    setExaminerSummary("Comparison completed, but no adaptive improvement value is available for the selected scenario.");
    return;
  }
  const queueImprovement =
    aggregate.mean_max_queue_improvement_pct === null || aggregate.mean_max_queue_improvement_pct === undefined
      ? "no max-queue percentage available"
      : `${signedNumber(aggregate.mean_max_queue_improvement_pct)}% max-queue change`;
  setExaminerSummary(
    `For ${activeScenarioLabel()}, adaptive control produced ${signedNumber(aggregate.mean_wait_improvement_pct)}% ` +
      `mean-wait change, ${signedNumber(aggregate.mean_completed_delta_vs_fixed)} completed vehicles versus fixed-time, ` +
      `${queueImprovement}, and ${aggregate.total_conflicting_green_violations} conflicting-green safety violations.`
  );
}

function applySummary(summary) {
  state.lastSummary = summary;
  elements.completed.textContent = summary.completed;
  elements.meanWait.textContent = `${summary.mean_wait_s.toFixed(1)}s`;
  elements.maxQueue.textContent = summary.max_queue;
  elements.violations.textContent = summary.conflicting_green_violations;
  elements.evidenceSafety.textContent =
    summary.conflicting_green_violations === 0
      ? "0 violations"
      : `${summary.conflicting_green_violations} violations`;
  elements.evidenceSafety.classList.toggle("benchmark-positive", summary.conflicting_green_violations === 0);
  elements.evidenceSafety.classList.toggle("benchmark-negative", summary.conflicting_green_violations !== 0);
  updateExaminerSummaryFromLiveRun(summary);
}

function applyEvidenceFromBenchmark(rows) {
  const selected = activeScenarioName();
  const adaptive = rows.find((row) => row.scenario === selected && row.controller === "adaptive");
  if (!adaptive || adaptive.mean_wait_improvement_pct === null || adaptive.mean_wait_improvement_pct === undefined) {
    elements.evidenceWait.textContent = "No comparison";
    elements.evidenceWait.className = "benchmark-negative";
    updateExaminerSummaryFromComparison();
    return;
  }
  const value = adaptive.mean_wait_improvement_pct;
  elements.evidenceWait.textContent = `${value >= 0 ? "+" : ""}${value.toFixed(1)}% wait`;
  elements.evidenceWait.className = value >= 0 ? "benchmark-positive" : "benchmark-negative";
  updateExaminerSummaryFromComparison();
}

function resetRunView() {
  state.maxQueue = 0;
  state.lastSummary = null;
  history.length = 0;
  elements.completed.textContent = "0";
  elements.meanWait.textContent = "-";
  elements.maxQueue.textContent = "0";
  elements.violations.textContent = "0";
  elements.faultActive.textContent = elements.faultProfile.value;
  elements.busiestApproach.textContent = "-";
  elements.detectorMismatch.textContent = "0";
  elements.detectorMismatch.className = "";
  setExaminerSummary("Run a simulation or comparison to generate a plain-English result summary.");
  elements.phase.textContent = "all_red_to_ns";
  elements.phaseTime.textContent = "0.0s";
  elements.reason.textContent = "startup";
  for (const approach of approaches) {
    const meter = document.querySelector(`#queue-${approach}`);
    const label = document.querySelector(`#queue-${approach}-value`);
    meter.max = 80;
    meter.value = 0;
    label.textContent = "0";
  }
  drawHistory();
  updateDetectorDemand({ north: 0, east: 0, south: 0, west: 0 });
  renderVehicles({ north: 0, east: 0, south: 0, west: 0 }, {});
  updateDemoNote();
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

async function loadScenarioCatalog() {
  try {
    const response = await fetch("/api/scenarios");
    if (!response.ok) {
      return;
    }
    state.scenarios = await response.json();
    updateScenarioDetails();
  } catch (error) {
    elements.scenarioDescription.textContent = "Scenario details could not be loaded.";
  }
}

async function loadFaultProfiles() {
  try {
    const response = await fetch(`/api/fault-profiles?duration_s=${encodeURIComponent(elements.duration.value)}`);
    if (!response.ok) {
      return;
    }
    state.faultProfiles = await response.json();
    updateFaultDetails();
  } catch (error) {
    elements.faultDescription.textContent = "Fault profile details could not be loaded.";
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

function improvementPct(baseline, candidate) {
  if (!baseline) {
    return null;
  }
  return ((baseline - candidate) / baseline) * 100;
}

function benchmarkSeeds() {
  const parsedBaseSeed = Number(elements.seed.value);
  const baseSeed = Number.isFinite(parsedBaseSeed) ? parsedBaseSeed : 1;
  const seedCount = Math.max(
    1,
    Math.min(50, Math.floor(Number(elements.benchmarkSeeds.value) || 1))
  );
  elements.seed.value = baseSeed;
  elements.benchmarkSeeds.value = seedCount;
  return Array.from({ length: seedCount }, (_, index) => baseSeed + index);
}

function renderAggregateCharts(aggregates) {
  drawGroupedChart(elements.benchmarkWaitChart, aggregates, {
    metric: "mean_wait_s",
    ciMetric: "ci95_wait_s",
    yLabel: "seconds",
    decimals: 1,
  });
  drawGroupedChart(elements.benchmarkQueueChart, aggregates, {
    metric: "mean_max_queue",
    ciMetric: "ci95_max_queue",
    yLabel: "vehicles",
    decimals: 1,
  });
}

function clearAggregateCharts() {
  drawChartPlaceholder(elements.benchmarkWaitChart, "Run a benchmark to chart mean wait");
  drawChartPlaceholder(elements.benchmarkQueueChart, "Run a benchmark to chart max queue");
}

function drawChartPlaceholder(svg, text) {
  svg.innerHTML = "";
  const label = svgElement("text", {
    x: 380,
    y: 136,
    "text-anchor": "middle",
    class: "chart-label",
  });
  label.textContent = text;
  svg.append(label);
}

function drawGroupedChart(svg, aggregates, options) {
  svg.innerHTML = "";
  if (!aggregates.length) {
    drawChartPlaceholder(svg, "No benchmark data");
    return;
  }

  const width = 760;
  const height = 260;
  const margin = { left: 50, right: 18, top: 18, bottom: 54 };
  const chartWidth = width - margin.left - margin.right;
  const chartHeight = height - margin.top - margin.bottom;
  const byKey = new Map(aggregates.map((row) => [`${row.scenario}:${row.controller}`, row]));
  const scenarios = benchmarkScenarios.filter((scenario) =>
    ["fixed", "adaptive"].some((controller) => byKey.has(`${scenario}:${controller}`))
  );
  for (const row of aggregates) {
    if (!scenarios.includes(row.scenario)) {
      scenarios.push(row.scenario);
    }
  }
  const maxValue = Math.max(
    1,
    ...aggregates.map((row) => Number(row[options.metric] || 0) + Number(row[options.ciMetric] || 0))
  );
  const groupWidth = chartWidth / Math.max(1, scenarios.length);
  const barWidth = Math.min(34, groupWidth * 0.26);

  svg.append(
    svgElement("line", {
      x1: margin.left,
      y1: margin.top,
      x2: margin.left,
      y2: margin.top + chartHeight,
      class: "chart-axis",
    })
  );
  svg.append(
    svgElement("line", {
      x1: margin.left,
      y1: margin.top + chartHeight,
      x2: width - margin.right,
      y2: margin.top + chartHeight,
      class: "chart-axis",
    })
  );

  for (let tick = 0; tick <= 4; tick += 1) {
    const value = (maxValue / 4) * tick;
    const y = margin.top + chartHeight - (value / maxValue) * chartHeight;
    svg.append(
      svgElement("line", {
        x1: margin.left - 4,
        y1: y,
        x2: width - margin.right,
        y2: y,
        class: tick === 0 ? "chart-axis" : "chart-grid",
      })
    );
    const tickLabel = svgElement("text", {
      x: margin.left - 8,
      y: y + 4,
      "text-anchor": "end",
      class: "chart-tick",
    });
    tickLabel.textContent = value.toFixed(0);
    svg.append(tickLabel);
  }

  const legend = [
    { controller: "fixed", label: "Fixed", className: "chart-bar-fixed", x: width - 170 },
    { controller: "adaptive", label: "Adaptive", className: "chart-bar-adaptive", x: width - 94 },
  ];
  for (const item of legend) {
    svg.append(svgElement("rect", { x: item.x, y: 10, width: 14, height: 14, rx: 3, class: item.className }));
    const label = svgElement("text", { x: item.x + 20, y: 22, class: "chart-legend" });
    label.textContent = item.label;
    svg.append(label);
  }

  for (const [index, scenario] of scenarios.entries()) {
    const centerX = margin.left + index * groupWidth + groupWidth / 2;
    const label = svgElement("text", {
      x: centerX,
      y: height - 26,
      "text-anchor": "middle",
      class: "chart-label",
    });
    label.textContent = scenario.replace("-", " ");
    svg.append(label);

    for (const item of [
      { controller: "fixed", className: "chart-bar chart-bar-fixed", offset: -barWidth * 0.62 },
      { controller: "adaptive", className: "chart-bar chart-bar-adaptive", offset: barWidth * 0.62 },
    ]) {
      const row = byKey.get(`${scenario}:${item.controller}`);
      if (!row) {
        continue;
      }
      const value = Number(row[options.metric] || 0);
      const ci95 = Number(row[options.ciMetric] || 0);
      const barHeight = (value / maxValue) * chartHeight;
      const x = centerX + item.offset - barWidth / 2;
      const y = margin.top + chartHeight - barHeight;
      svg.append(
        svgElement("rect", {
          x: x,
          y: y,
          width: barWidth,
          height: barHeight,
          rx: 4,
          class: item.className,
        })
      );

      if (ci95 > 0) {
        const yHigh = margin.top + chartHeight - ((value + ci95) / maxValue) * chartHeight;
        const yLow = margin.top + chartHeight - (Math.max(0, value - ci95) / maxValue) * chartHeight;
        const cx = x + barWidth / 2;
        svg.append(svgElement("line", { x1: cx, y1: yHigh, x2: cx, y2: yLow, class: "chart-ci" }));
        svg.append(svgElement("line", { x1: cx - 5, y1: yHigh, x2: cx + 5, y2: yHigh, class: "chart-ci" }));
        svg.append(svgElement("line", { x1: cx - 5, y1: yLow, x2: cx + 5, y2: yLow, class: "chart-ci" }));
      }

      const valueLabel = svgElement("text", {
        x: x + barWidth / 2,
        y: Math.max(12, y - 6),
        "text-anchor": "middle",
        class: "chart-value",
      });
      valueLabel.textContent = value.toFixed(options.decimals);
      svg.append(valueLabel);
    }
  }

  const axisLabel = svgElement("text", { x: margin.left, y: 12, class: "chart-label" });
  axisLabel.textContent = options.yLabel;
  svg.append(axisLabel);
}

async function runBenchmark() {
  await runBenchmarkForScenarios(benchmarkScenarios, "Running");
}

async function runSelectedComparison() {
  if (elements.customEnabled.checked) {
    await runCustomComparison();
    return;
  }
  await runBenchmarkForScenarios([elements.scenario.value], "Comparing selected scenario");
}

function appendBenchmarkRow(row) {
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

function customSimulationBody(controller) {
  return {
    controller,
    scenario: "custom-dashboard",
    fault_profile: elements.faultProfile.value,
    duration_s: Number(elements.duration.value),
    step_s: Number(elements.step.value),
    seed: Number(elements.seed.value),
    persist: false,
    custom_arrivals_per_minute: customArrivals(),
  };
}

async function fetchSimulationSummary(controller) {
  const response = await fetch("/api/simulations", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(customSimulationBody(controller)),
  });
  if (!response.ok) {
    throw new Error(`Simulation failed with status ${response.status}`);
  }
  return response.json();
}

function customComparisonPayload(fixed, adaptive) {
  const waitImprovement = improvementPct(fixed.mean_wait_s, adaptive.mean_wait_s);
  const queueImprovement = improvementPct(fixed.max_queue, adaptive.max_queue);
  const completedDelta = adaptive.completed - fixed.completed;
  const seed = Number(elements.seed.value);
  const rows = [
    {
      scenario: "custom-dashboard",
      seed,
      controller: "fixed",
      arrivals: fixed.arrivals,
      completed: fixed.completed,
      throughput_veh_per_min: fixed.throughput_veh_per_min,
      mean_wait_s: fixed.mean_wait_s,
      max_queue: fixed.max_queue,
      conflicting_green_violations: fixed.conflicting_green_violations,
      completed_delta_vs_fixed: null,
      mean_wait_improvement_pct: null,
      max_queue_improvement_pct: null,
    },
    {
      scenario: "custom-dashboard",
      seed,
      controller: "adaptive",
      arrivals: adaptive.arrivals,
      completed: adaptive.completed,
      throughput_veh_per_min: adaptive.throughput_veh_per_min,
      mean_wait_s: adaptive.mean_wait_s,
      max_queue: adaptive.max_queue,
      conflicting_green_violations: adaptive.conflicting_green_violations,
      completed_delta_vs_fixed: completedDelta,
      mean_wait_improvement_pct: waitImprovement,
      max_queue_improvement_pct: queueImprovement,
    },
  ];
  const aggregates = rows.map((row) => ({
    scenario: row.scenario,
    controller: row.controller,
    runs: 1,
    mean_completed: row.completed,
    std_completed: 0,
    ci95_completed: 0,
    mean_wait_s: row.mean_wait_s,
    std_wait_s: 0,
    ci95_wait_s: 0,
    mean_max_queue: row.max_queue,
    std_max_queue: 0,
    ci95_max_queue: 0,
    total_conflicting_green_violations: row.conflicting_green_violations,
    mean_completed_delta_vs_fixed: row.completed_delta_vs_fixed,
    std_completed_delta_vs_fixed: 0,
    ci95_completed_delta_vs_fixed: 0,
    mean_wait_improvement_pct: row.mean_wait_improvement_pct,
    std_wait_improvement_pct: 0,
    ci95_wait_improvement_pct: 0,
    mean_max_queue_improvement_pct: row.max_queue_improvement_pct,
    std_max_queue_improvement_pct: 0,
    ci95_max_queue_improvement_pct: 0,
  }));
  return { rows, aggregates };
}

async function runCustomComparison() {
  setBenchmarkRunning(true);
  elements.benchmarkStatus.textContent = "Comparing custom scenario";
  elements.benchmarkBody.innerHTML = "";
  clearAggregateCharts();
  try {
    const [fixed, adaptive] = await Promise.all([
      fetchSimulationSummary("fixed"),
      fetchSimulationSummary("adaptive"),
    ]);
    const payload = customComparisonPayload(fixed, adaptive);
    state.lastBenchmarkRows = payload.rows;
    state.lastBenchmarkAggregates = payload.aggregates;
    for (const row of payload.rows) {
      appendBenchmarkRow(row);
    }
    renderAggregateCharts(payload.aggregates);
    applyEvidenceFromBenchmark(payload.rows);
    elements.benchmarkStatus.textContent = "Custom fixed/adaptive comparison";
  } catch (error) {
    elements.benchmarkStatus.textContent = "Failed";
  } finally {
    setBenchmarkRunning(false);
  }
}

async function runBenchmarkForScenarios(scenarios, runningLabel) {
  setBenchmarkRunning(true);
  elements.benchmarkStatus.textContent = runningLabel;
  elements.benchmarkBody.innerHTML = "";
  clearAggregateCharts();
  const seeds = benchmarkSeeds();
  try {
    const response = await fetch("/api/benchmarks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        scenarios,
        seeds,
        duration_s: Number(elements.duration.value),
        step_s: Number(elements.step.value),
      }),
    });
    if (!response.ok) {
      throw new Error(`Benchmark failed with status ${response.status}`);
    }
    const payload = await response.json();
    state.lastBenchmarkRows = payload.rows;
    state.lastBenchmarkAggregates = payload.aggregates;
    for (const row of payload.rows) {
      appendBenchmarkRow(row);
    }
    renderAggregateCharts(payload.aggregates);
    applyEvidenceFromBenchmark(payload.rows);
    elements.benchmarkStatus.textContent = `${payload.rows.length} rows, ${seeds.length} seeds`;
  } catch (error) {
    elements.benchmarkStatus.textContent = "Failed";
  } finally {
    setBenchmarkRunning(false);
  }
}

function runSimulation(options = {}) {
  if (state.running) {
    return Promise.resolve(null);
  }
  resetRunView();
  setRunning(true);
  setStatus("Connecting");
  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  const socket = new WebSocket(`${protocol}://${window.location.host}/ws/simulation?${params(options.persist ?? "true")}`);
  state.socket = socket;
  let resolved = false;

  return new Promise((resolve, reject) => {
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
        resolved = true;
        resolve(message.summary);
      }
    });
    socket.addEventListener("close", () => {
      setRunning(false);
      state.socket = null;
      if (!resolved) {
        resolve(null);
      }
    });
    socket.addEventListener("error", () => {
      setStatus("Connection error");
      setRunning(false);
      if (!resolved) {
        reject(new Error("Simulation connection error"));
      }
    });
  });
}

function setControls(preset) {
  elements.customEnabled.checked = false;
  elements.controller.value = preset.controller;
  elements.scenario.value = preset.scenario;
  elements.faultProfile.value = preset.faultProfile;
  elements.duration.value = preset.duration;
  elements.step.value = preset.step;
  elements.seed.value = preset.seed;
  loadFaultProfiles();
}

function delay(ms) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

async function runDemoTour() {
  if (state.running) {
    return;
  }
  elements.tourButton.disabled = true;
  elements.tourButton.textContent = "Tour running";
  try {
    setStatus("Tour: adaptive heavy demand");
    setControls({ ...presetConfig["adaptive-ns"], duration: 60 });
    await runSimulation();
    await delay(500);
    setStatus("Tour: detector fault");
    setControls({ ...presetConfig.fault, duration: 60 });
    await runSimulation();
    await delay(500);
    setStatus("Tour: selected comparison");
    elements.benchmarkSeeds.value = 5;
    await runSelectedComparison();
    setStatus("Tour complete");
  } finally {
    elements.tourButton.disabled = false;
    elements.tourButton.textContent = "Run Demo Tour";
  }
}

function applyPreset(name) {
  const preset = presetConfig[name];
  if (!preset) {
    return;
  }
  stopSimulation();
  setControls(preset);
  resetRunView();
  runSimulation();
}

function selectedAdaptiveAggregate() {
  const selected = activeScenarioName();
  return state.lastBenchmarkAggregates.find(
    (row) => row.scenario === selected && row.controller === "adaptive"
  );
}

function evidenceSummaryText() {
  const lines = [
    "Simulation-Based Adaptive Smart Traffic-Light Controller Evidence",
    "",
    `Controller: ${elements.controller.value}`,
    `Scenario: ${activeScenarioLabel()}`,
    `Fault profile: ${elements.faultProfile.value}`,
    `Duration: ${elements.duration.value}s`,
    `Step: ${elements.step.value}s`,
    `Seed: ${elements.seed.value}`,
    "",
    "Live run:",
  ];

  if (state.lastSummary) {
    lines.push(
      `Completed vehicles: ${state.lastSummary.completed}`,
      `Mean wait: ${state.lastSummary.mean_wait_s.toFixed(2)}s`,
      `Max queue: ${state.lastSummary.max_queue}`,
      `Safety violations: ${state.lastSummary.conflicting_green_violations}`
    );
  } else {
    lines.push("No completed live run captured in this dashboard session.");
  }

  lines.push("", "Current dashboard evidence:");
  lines.push(
    `Safety badge: ${elements.evidenceSafety.textContent}`,
    `Wait result badge: ${elements.evidenceWait.textContent}`,
    `Detector fault badge: ${elements.evidenceFault.textContent}`,
    `Busiest approach: ${elements.busiestApproach.textContent}`,
    `Detector mismatch: ${elements.detectorMismatch.textContent}`,
    `Examiner summary: ${elements.examinerSummary.textContent}`
  );

  const aggregate = selectedAdaptiveAggregate();
  lines.push("", "Selected scenario benchmark:");
  if (aggregate && aggregate.mean_wait_improvement_pct !== null && aggregate.mean_wait_improvement_pct !== undefined) {
    const queueImprovement =
      aggregate.mean_max_queue_improvement_pct === null || aggregate.mean_max_queue_improvement_pct === undefined
        ? "-"
        : `${aggregate.mean_max_queue_improvement_pct.toFixed(2)}%`;
    lines.push(
      `Adaptive mean wait improvement: ${aggregate.mean_wait_improvement_pct.toFixed(2)}%`,
      `Adaptive completed delta vs fixed: ${aggregate.mean_completed_delta_vs_fixed.toFixed(2)}`,
      `Adaptive max queue improvement: ${queueImprovement}`,
      `Aggregate safety violations: ${aggregate.total_conflicting_green_violations}`,
      `Benchmark runs: ${aggregate.runs}`
    );
  } else {
    lines.push("Run Compare Selected or Benchmark to capture fixed/adaptive evidence.");
  }

  return lines.join("\n");
}

function downloadEvidenceText(text) {
  const blob = new Blob([text], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "traffic-light-dashboard-evidence.txt";
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

async function copyEvidenceSummary() {
  const text = evidenceSummaryText();
  try {
    await navigator.clipboard.writeText(text);
    setStatus("Evidence copied");
  } catch (error) {
    downloadEvidenceText(text);
    setStatus("Evidence downloaded");
  }
}

function stopSimulation() {
  if (state.socket) {
    state.socket.close();
    state.socket = null;
  }
  setStatus("Stopped");
  setRunning(false);
}

function resetDashboard() {
  stopSimulation();
  setStatus("Idle");
  resetRunView();
}

elements.runButton.addEventListener("click", runSimulation);
elements.stopButton.addEventListener("click", stopSimulation);
elements.resetButton.addEventListener("click", resetDashboard);
elements.benchmarkButton.addEventListener("click", runBenchmark);
elements.compareButton.addEventListener("click", runSelectedComparison);
elements.tourButton.addEventListener("click", runDemoTour);
elements.copyEvidenceButton.addEventListener("click", copyEvidenceSummary);
elements.controller.addEventListener("change", updateDemoNote);
elements.scenario.addEventListener("change", updateDemoNote);
elements.customEnabled.addEventListener("change", updateDemoNote);
for (const input of [elements.customNorth, elements.customEast, elements.customSouth, elements.customWest]) {
  input.addEventListener("input", updateDemoNote);
}
elements.faultProfile.addEventListener("change", updateDemoNote);
elements.duration.addEventListener("change", loadFaultProfiles);
for (const button of elements.presetButtons) {
  button.addEventListener("click", () => applyPreset(button.dataset.preset));
}
activateSignals({ north: "red", east: "red", west: "red", south: "red" });
renderVehicles({ north: 0, east: 0, south: 0, west: 0 }, {});
clearAggregateCharts();
updateDemoNote();
loadRuns();
loadScenarioCatalog();
loadFaultProfiles();
