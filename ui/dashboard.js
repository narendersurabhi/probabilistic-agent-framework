const statusEl = document.getElementById('status');
const timelineEl = document.getElementById('timeline');
const beliefEl = document.getElementById('beliefState');
const policyEl = document.getElementById('policyProbs');
const efeEl = document.getElementById('efe');
const toolsEl = document.getElementById('tools');
const benchmarkEl = document.getElementById('benchmark');

async function runTask() {
  const query = document.getElementById('queryInput').value;
  statusEl.textContent = 'Running...';
  await fetch('/run_task', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query })
  });
  statusEl.textContent = 'Task submitted. Polling updates every 500ms.';
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

async function refresh() {
  const [stepsRes, beliefRes, benchmarkRes] = await Promise.all([
    fetch('/agent_steps'),
    fetch('/belief_state'),
    fetch('/benchmark_results')
  ]);

  const steps = await stepsRes.json();
  const belief = await beliefRes.json();
  const benchmark = await benchmarkRes.json();

  renderTimeline(steps);
  beliefEl.textContent = JSON.stringify(belief, null, 2);
  benchmarkEl.textContent = JSON.stringify(benchmark, null, 2);

  if (steps.length > 0) {
    const latest = steps[steps.length - 1];
    policyEl.textContent = JSON.stringify(latest.policy_probabilities, null, 2);
    efeEl.textContent = JSON.stringify(latest.expected_free_energy, null, 2);
    toolsEl.textContent = JSON.stringify(latest.tool_execution, null, 2);
  } else {
    policyEl.textContent = '{}';
    efeEl.textContent = '{}';
    toolsEl.textContent = '{}';
  }
}

document.getElementById('runBtn').addEventListener('click', runTask);
setInterval(refresh, 500);
refresh();
