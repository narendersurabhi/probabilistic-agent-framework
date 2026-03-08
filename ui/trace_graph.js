const traceStatusEl = document.getElementById('traceStatus');
const metadataEl = document.getElementById('nodeMetadata');
const svg = d3.select('#traceGraph');

const nodeColors = {
  query: '#3b82f6',
  belief_update: '#7c3aed',
  policy_eval: '#f59e0b',
  action_selection: '#10b981',
  tool_execution: '#eab308',
  observation: '#6b7280',
  critic: '#ef4444',
};

function drawGraph(trace) {
  svg.selectAll('*').remove();

  const width = document.getElementById('traceGraph').clientWidth || 900;
  const height = 520;

  const container = svg.append('g');
  svg.call(
    d3.zoom().scaleExtent([0.4, 3]).on('zoom', (event) => {
      container.attr('transform', event.transform);
    })
  );

  const simulation = d3
    .forceSimulation(trace.nodes)
    .force('link', d3.forceLink(trace.edges).id((d) => d.id).distance(120))
    .force('charge', d3.forceManyBody().strength(-450))
    .force('center', d3.forceCenter(width / 2, height / 2));

  const link = container
    .append('g')
    .attr('stroke', '#9ca3af')
    .selectAll('line')
    .data(trace.edges)
    .join('line')
    .attr('stroke-width', 1.5);

  const node = container
    .append('g')
    .selectAll('g')
    .data(trace.nodes)
    .join('g')
    .style('cursor', 'pointer')
    .on('click', (_, d) => {
      metadataEl.textContent = JSON.stringify({ id: d.id, type: d.type, label: d.label, data: d.data }, null, 2);
    })
    .call(
      d3
        .drag()
        .on('start', (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on('drag', (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on('end', (event, d) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        })
    );

  node
    .append('circle')
    .attr('r', 20)
    .attr('fill', (d) => nodeColors[d.type] || '#111827');

  node
    .append('text')
    .text((d) => d.label.length > 16 ? `${d.label.slice(0, 16)}...` : d.label)
    .attr('x', 24)
    .attr('y', 5)
    .style('font-size', '11px');

  simulation.on('tick', () => {
    link
      .attr('x1', (d) => d.source.x)
      .attr('y1', (d) => d.source.y)
      .attr('x2', (d) => d.target.x)
      .attr('y2', (d) => d.target.y);

    node.attr('transform', (d) => `translate(${d.x},${d.y})`);
  });
}

async function loadTrace(runId) {
  if (!runId) {
    traceStatusEl.textContent = 'Please enter a run ID.';
    return;
  }
  traceStatusEl.textContent = `Loading trace ${runId}...`;
  try {
    const response = await fetch(`/trace/${runId}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const trace = await response.json();
    drawGraph(trace);
    traceStatusEl.textContent = `Loaded trace ${runId} (${trace.nodes.length} nodes, ${trace.edges.length} edges).`;
  } catch (err) {
    traceStatusEl.textContent = `Failed to load trace: ${err}`;
  }
}

async function autoLoadLatest() {
  try {
    const beliefRes = await fetch('/belief_state');
    const belief = await beliefRes.json();
    const runId = belief.last_run_id;
    if (runId) {
      document.getElementById('runIdInput').value = runId;
      await loadTrace(runId);
      return;
    }
  } catch (err) {
    // ignore auto-load errors
  }
  traceStatusEl.textContent = 'No run found yet. Execute a task from the main dashboard, then load its run_id.';
}

document.getElementById('loadTraceBtn').addEventListener('click', () => {
  const runId = document.getElementById('runIdInput').value.trim();
  loadTrace(runId);
});

autoLoadLatest();
