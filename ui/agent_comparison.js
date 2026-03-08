const gridEl = document.getElementById('comparisonGrid');
const summaryEl = document.getElementById('summary');

function renderAgentCard(title, payload) {
  const steps = payload.steps || [];
  const card = document.createElement('div');
  card.className = 'panel';

  const blocks = steps
    .map((step) => {
      const policy = step.policy_probabilities
        ? `<pre>${JSON.stringify(step.policy_probabilities, null, 2)}</pre>`
        : '';
      return `
        <div class="step">
          <strong>Step ${step.step}: ${step.action || 'n/a'}</strong>
          <br/>Args: ${JSON.stringify(step.arguments || {})}
          <br/>Observation: ${JSON.stringify(step.observation || {})}
          ${policy ? `<br/>Policy probabilities:${policy}` : ''}
        </div>
      `;
    })
    .join('');

  card.innerHTML = `<h2>${title}</h2>${blocks || '<p>No steps returned.</p>'}`;
  gridEl.appendChild(card);
}

async function runComparison() {
  const taskId = document.getElementById('taskId').value || 'task_001';
  const query = document.getElementById('query').value;
  const resp = await fetch('/compare_agents', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ task_id: taskId, query })
  });
  const payload = await resp.json();

  summaryEl.textContent = JSON.stringify({
    task_id: payload.task_id,
    query: payload.query,
    artifact_path: payload.artifact_path
  }, null, 2);

  gridEl.innerHTML = '';
  renderAgentCard('Standard Agent', payload.standard_agent || {});
  renderAgentCard('ReAct Agent', payload.react_agent || {});
  renderAgentCard('Active Inference Agent', payload.active_inference_agent || {});
}

document.getElementById('runCompare').addEventListener('click', runComparison);
runComparison();
