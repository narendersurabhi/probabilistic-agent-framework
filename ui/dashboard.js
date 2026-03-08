const statusEl = document.getElementById('status');
const timelineEl = document.getElementById('timeline');
const beliefEl = document.getElementById('beliefState');
const policyEl = document.getElementById('policyProbs');
const efeEl = document.getElementById('efe');
const toolsEl = document.getElementById('tools');
const benchmarkEl = document.getElementById('benchmark');
const queryTextEl = document.getElementById('currentQuery');
const wsStateEl = document.getElementById('wsState');
const actionHistoryEl = document.getElementById('actionHistory');
const graphNodesEl = document.getElementById('graphNodes');
const comparisonEl = document.getElementById('agentComparison');
const failureEl = document.getElementById('failureAnalysis');
const arenaEl = document.getElementById('arenaResults');

const events = [];
const graph = { nodes: [], edges: [] };
let socket = null;

const beliefChart = new Chart(document.getElementById('beliefChart'), {
  type: 'bar',
  data: {
    labels: ['unknown', 'partial', 'confident'],
    datasets: [{ label: 'Knowledge Belief', data: [0.7, 0.2, 0.1], backgroundColor: '#4f46e5' }]
  },
  options: { animation: false, responsive: true, scales: { y: { min: 0, max: 1 } } }
});

const policyChart = new Chart(document.getElementById('policyChart'), {
  type: 'bar',
  data: {
    labels: ['retrieve_docs', 'call_calculator', 'generate_answer'],
    datasets: [{ label: 'Policy Probabilities', data: [0, 0, 0], backgroundColor: '#059669' }]
  },
  options: { animation: false, responsive: true, scales: { y: { min: 0, max: 1 } } }
});

function addGraphNode(label) {
  const id = `n_${graph.nodes.length + 1}`;
  graph.nodes.push({ id, label });
  if (graph.nodes.length > 1) {
    graph.edges.push({ from: graph.nodes[graph.nodes.length - 2].id, to: id });
  }
  graphNodesEl.textContent = JSON.stringify(graph, null, 2);
}

function renderTimeline(steps) {
  timelineEl.innerHTML = '';
  steps.forEach((s) => {
    const div = document.createElement('div');
    div.className = 'step';
    div.innerHTML = `<strong>Step ${s.step}</strong><br/>Action: ${s.action}`;
    timelineEl.appendChild(div);
  });
}

function handleStepEvent(data) {
  if (data.query) {
    queryTextEl.textContent = data.query;
  }
  beliefEl.textContent = JSON.stringify(data.belief_state || {}, null, 2);
  policyEl.textContent = JSON.stringify(data.policy_probabilities || {}, null, 2);
  efeEl.textContent = JSON.stringify(data.expected_free_energy || {}, null, 2);
  toolsEl.textContent = JSON.stringify(data.tool_execution || data.observation || {}, null, 2);

  const k = data.belief_state?.knowledge_state || {};
  beliefChart.data.datasets[0].data = [k.unknown || 0, k.partial || 0, k.confident || 0];
  beliefChart.update();

  const p = data.policy_probabilities || {};
  policyChart.data.datasets[0].data = [p.retrieve_docs || 0, p.call_calculator || 0, p.generate_answer || 0];
  policyChart.update();

  if (data.action) {
    const li = document.createElement('li');
    li.textContent = `Step ${data.step}: ${data.action}`;
    actionHistoryEl.appendChild(li);
    addGraphNode(data.action);
  }
}

function connectWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
  socket = new WebSocket(`${protocol}://${window.location.host}/stream`);

  socket.onopen = () => {
    wsStateEl.textContent = 'connected';
    setInterval(() => {
      if (socket?.readyState === WebSocket.OPEN) {
        socket.send('ping');
      }
    }, 1000);
  };

  socket.onclose = () => {
    wsStateEl.textContent = 'disconnected';
    setTimeout(connectWebSocket, 1000);
  };

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    events.push(data);
    if (data.event === 'agent_step' || data.event === 'benchmark_step') {
      handleStepEvent(data);
    }
    if (data.event === 'task_started') {
      statusEl.textContent = `Task ${data.task_id} started.`;
      actionHistoryEl.innerHTML = '';
      graph.nodes = [];
      graph.edges = [];
    }
    if (data.event === 'task_completed') {
      statusEl.textContent = `Task ${data.task_id} completed in ${data.steps} steps.`;
    }
    if (data.event === 'benchmark_completed') {
      benchmarkEl.textContent = JSON.stringify(data.results, null, 2);
      refresh();
    }
    if (data.event === 'arena_completed') {
      arenaEl.textContent = JSON.stringify(data.results.leaderboard || data.results, null, 2);
      statusEl.textContent = 'Agent Arena completed.';
      refresh();
    }
  };
}

async function runTask() {
  const query = document.getElementById('queryInput').value;
  statusEl.textContent = 'Running...';
  await fetch('/run_task', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query })
  });
}

async function runBenchmark() {
  statusEl.textContent = 'Running benchmark...';
  await fetch('/run_benchmark', { method: 'POST' });
}

async function runArena() {
  statusEl.textContent = 'Running arena...';
  await fetch('/run_arena', { method: 'POST' });
}

async function compareAgents() {
  const taskId = document.getElementById('comparisonTaskId').value || 'task_001';
  const query = document.getElementById('comparisonQuery').value;
  const resp = await fetch('/compare_agents', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ task_id: taskId, query })
  });
  const payload = await resp.json();
  comparisonEl.textContent = JSON.stringify(payload, null, 2);
}

async function refresh() {
  const [stepsRes, beliefRes, benchmarkRes, failureRes, arenaRes] = await Promise.all([
    fetch('/agent_steps'),
    fetch('/belief_state'),
    fetch('/benchmark_results'),
    fetch('/failure_analysis'),
    fetch('/arena_results')
  ]);

  const steps = await stepsRes.json();
  const belief = await beliefRes.json();
  const benchmark = await benchmarkRes.json();
  const failure = await failureRes.json();
  const arena = await arenaRes.json();

  renderTimeline(steps);
  beliefEl.textContent = JSON.stringify(belief, null, 2);
  benchmarkEl.textContent = JSON.stringify(benchmark, null, 2);
  failureEl.textContent = JSON.stringify(failure, null, 2);
  arenaEl.textContent = JSON.stringify(arena.leaderboard || arena, null, 2);
}

document.getElementById('runBtn').addEventListener('click', runTask);
document.getElementById('benchmarkBtn').addEventListener('click', runBenchmark);
document.getElementById('arenaBtn').addEventListener('click', runArena);
document.getElementById('compareBtn').addEventListener('click', compareAgents);
setInterval(refresh, 1000);
connectWebSocket();
refresh();
