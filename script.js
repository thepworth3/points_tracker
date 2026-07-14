async function loadScoreboard() {
  const res = await fetch('data.json', { cache: 'no-store' });
  const data = await res.json();

  const categories = data.categories || [];
  const players = data.players || {};

  const totals = Object.entries(players).map(([name, scores]) => {
    const total = categories.reduce((sum, cat) => sum + (scores[cat] || 0), 0);
    return { name, scores, total };
  }).sort((a, b) => b.total - a.total);

  renderPodium(totals);
  renderMatrix(categories, totals);

  document.getElementById('categoryCount').textContent =
    `${totals.length} competitor${totals.length === 1 ? '' : 's'} · ${categories.length} category${categories.length === 1 ? '' : 'ies'}`;

  if (data.updated) {
    const d = new Date(data.updated);
    document.getElementById('updatedStamp').textContent =
      `— updated ${d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })} —`;
  }
}

function renderPodium(totals) {
  const el = document.getElementById('podium');
  el.innerHTML = totals.map((p, i) => `
    <div class="rank-row rank-row--${i + 1}">
      <div class="rank-badge">${i + 1}</div>
      <div class="rank-name">${escapeHtml(p.name)}</div>
      <div class="rank-total">${p.total}</div>
    </div>
  `).join('');
}

function renderMatrix(categories, totals) {
  const table = document.getElementById('matrix');
  const thead = table.querySelector('thead tr');
  const tbody = table.querySelector('tbody');

  thead.innerHTML = '<th class="matrix__corner">player</th>' +
    categories.map(c => `<th>${escapeHtml(c)}</th>`).join('') +
    '<th>total</th>';

  // find category leaders for highlight
  const leaders = {};
  categories.forEach(cat => {
    let best = -Infinity;
    totals.forEach(p => { if ((p.scores[cat] || 0) > best) best = p.scores[cat] || 0; });
    leaders[cat] = best;
  });

  tbody.innerHTML = totals.map(p => `
    <tr>
      <td>${escapeHtml(p.name)}</td>
      ${categories.map(cat => {
        const val = p.scores[cat] || 0;
        const isLeader = val === leaders[cat] && val > 0;
        return `<td class="${isLeader ? 'leader-cell' : ''}">${val}</td>`;
      }).join('')}
      <td><strong>${p.total}</strong></td>
    </tr>
  `).join('');
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

loadScoreboard().catch(err => {
  document.body.innerHTML = `<p style="color:#e0705a;font-family:monospace;padding:40px;text-align:center">
    Couldn't load data.json — ${err.message}
  </p>`;
});
