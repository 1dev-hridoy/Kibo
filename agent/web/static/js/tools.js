let toolsData = [];

function toolGroup(name) {
  if (/^(web_search|fetch_url|download_file|dns_|whois|ip_geo)/.test(name)) return 'Internet';
  if (/port_scan|network_scan|subnet|arp|vpn|wifi|listener|network_details|ping|scan_nearby/.test(name)) return 'Network';
  if (/hash|jwt|pcap|apk|checksum|identify_hash|search_content|audit_website|subdomain/.test(name)) return 'Security';
  if (/volume|brightness|screenshot|battery|clipboard|lock|speak|photo|webcam/.test(name)) return 'System control';
  if (/file|directory|folder|disk|process|model|memory|health/.test(name)) return 'Files & apps';
  if (/voice|widget|macro|screen|terminal|read_file|write_file|search/.test(name)) return 'Automation';
  return 'Other';
}

function renderTools(filter) {
  const q = (filter || '').toLowerCase();
  const wrap = document.getElementById('tool-list');
  const groups = {};
  toolsData
    .filter(t => !q || t.name.includes(q) || (t.description || '').toLowerCase().includes(q))
    .forEach(t => {
      const g = toolGroup(t.name);
      (groups[g] = groups[g] || []).push(t);
    });
  wrap.innerHTML = '';
  Object.keys(groups).sort().forEach(g => {
    const head = document.createElement('div');
    head.className = 'tool-group text-muted mt-3 mb-1';
    head.textContent = g + ' (' + groups[g].length + ')';
    wrap.appendChild(head);
    const row = document.createElement('div');
    row.className = 'd-flex flex-wrap gap-2';
    groups[g].forEach(t => {
      const span = document.createElement('span');
      span.className = 'tool-pill';
      span.title = t.description || '';
      span.textContent = t.name;
      row.appendChild(span);
    });
    wrap.appendChild(row);
  });
  const count = toolsData.filter(t => !q || t.name.includes(q)).length;
  document.getElementById('tool-count').textContent = count + ' of ' + toolsData.length + ' tools';
}

async function loadTools() {
  try {
    const res = await fetch('/api/tools');
    const data = await res.json();
    toolsData = (data.tools || []).map(t => typeof t === 'string' ? { name: t, description: '' } : t);
    renderTools('');
  } catch (e) {
    document.getElementById('tool-list').innerHTML = '<div class="text-danger mt-3">Failed to load tools.</div>';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const box = document.getElementById('tool-search');
  box.addEventListener('input', () => renderTools(box.value.trim()));
  loadTools();
});
