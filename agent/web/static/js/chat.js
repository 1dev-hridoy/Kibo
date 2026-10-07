const COMMANDS = [
  { cmd: '/help', label: 'Show what I can do', send: 'What can you do' },
  { cmd: '/tools', label: 'Open tools page', href: '/tools' },
  { cmd: '/screenshot', label: 'Take a screenshot', send: 'Take a screenshot' },
  { cmd: '/battery', label: 'Check battery', send: 'Check battery status' },
  { cmd: '/volume', label: 'Get volume level', send: 'Get volume levels' },
  { cmd: '/bright', label: 'Set brightness 80%', send: 'Set brightness to 80' },
  { cmd: '/wifi', label: 'WiFi info', send: 'WiFi info' },
  { cmd: '/procs', label: 'Running processes', send: 'Show running processes' },
  { cmd: '/disk', label: 'Disk usage', send: 'Show disk usage' },
  { cmd: '/lock', label: 'Lock screen', send: 'Lock the screen' },
  { cmd: '/models', label: 'Switch model', action: 'models' },
  { cmd: '/live', label: 'Live screen', action: 'live' },
  { cmd: '/term', label: 'Open terminal', action: 'term' },
  { cmd: '/macros', label: 'Macros', action: 'macros' },
  { cmd: '/clear', label: 'Clear chat', action: 'clear' },
  { cmd: '/history', label: 'Load history', action: 'history' }
];

function renderToolsCard(tools) {
  if (!tools || !tools.length) return '';
  const names = tools.map(t => '<div><span class="tool-name">&#9881;</span> ' + esc(t) + '</div>').join('');
  return '<div class="tool-card"><strong>' + tools.length + ' tool call' + (tools.length > 1 ? 's' : '') + '</strong>' + names + '</div>';
}

function renderMediaCard(media) {
  if (!media || !media.url) return '';
  return '<div class="media-card"><div class="media-head">' + esc(media.type || 'image') +
    '</div><img src="' + esc(media.url) + '" alt="attachment" onclick="window.open(this.src)"></div>';
}

function renderError(err) {
  return '<div class="error-card">&#9888; ' + esc(err) + '</div>';
}

async function loadModel() {
  try {
    const res = await fetch('/api/model');
    const data = await res.json();
    const el = document.getElementById('model-name');
    if (el) el.textContent = (data.name || data.active || '?') + (data.size ? ' (' + data.size + ')' : '');
  } catch (e) {}
}

async function showModelPicker() {
  const list = document.getElementById('model-list');
  document.getElementById('model-dialog').showModal();
  list.innerHTML = '<div class="text-muted small">Loading...</div>';
  try {
    const res = await fetch('/api/models');
    const data = await res.json();
    list.innerHTML = '';
    data.models.forEach(m => {
      const btn = document.createElement('button');
      btn.className = 'btn w-100 text-start mb-2';
      btn.disabled = !m.available || m.active;
      btn.innerHTML = (m.active ? '&#9679; ' : '&#9675; ') + esc(m.name) + ' <span class="text-muted small">' + esc(m.size) + '</span>' +
        (m.available ? '' : ' <span class="text-danger small">not downloaded</span>');
      btn.onclick = async () => {
        await fetch('/api/model', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ model: m.key }) });
        document.getElementById('model-dialog').close();
        loadModel();
        addMsg('Kibo', 'agent', 'Switched to ' + esc(m.name));
      };
      list.appendChild(btn);
    });
  } catch (e) {
    list.innerHTML = '<div class="text-danger small">Error loading models</div>';
  }
}

async function sendChat(text) {
  addMsg('You', 'user', esc(text));
  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    });
    const data = await res.json();
    if (data.error) {
      addMsg('Kibo', 'agent', renderError(data.error));
      return;
    }
    let html = esc(data.response || '...');
    html += renderMediaCard(data.media);
    html += renderToolsCard(data.tools);
    addMsg('Kibo', 'agent', html);
  } catch (err) {
    addMsg('Kibo', 'agent', renderError(err.message));
  }
}

function sendCmd(text) {
  const input = document.getElementById('input');
  input.value = '';
  hideCmdMenu();
  sendChat(text);
}

function showCmdMenu(filter) {
  const menu = document.getElementById('cmd-menu');
  const q = (filter || '').toLowerCase();
  const items = COMMANDS.filter(c => !q || c.cmd.startsWith(q));
  menu.innerHTML = '';
  items.forEach(c => {
    const div = document.createElement('div');
    div.className = 'cmd-item';
    div.innerHTML = '<code>' + esc(c.cmd) + '</code> <span class="text-muted">' + esc(c.label) + '</span>';
    div.onclick = () => runCommand(c);
    menu.appendChild(div);
  });
  menu.classList.toggle('d-none', items.length === 0);
}

function hideCmdMenu() {
  document.getElementById('cmd-menu').classList.add('d-none');
}

function runCommand(c) {
  if (c.href) { window.location.href = c.href; return; }
  if (c.action === 'models') { hideCmdMenu(); showModelPicker(); return; }
  if (c.action === 'live') { hideCmdMenu(); document.getElementById('screen-dialog').showModal(); return; }
  if (c.action === 'term') { hideCmdMenu(); openTerminal(); return; }
  if (c.action === 'macros') { hideCmdMenu(); loadMacros(); document.getElementById('macro-dialog').showModal(); return; }
  if (c.action === 'clear') { hideCmdMenu(); clearChat(); return; }
  if (c.action === 'history') { hideCmdMenu(); clearChat(); loadHistory(); return; }
  sendCmd(c.send);
}

document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('input');
  const form = document.getElementById('chat');
  input.addEventListener('input', () => {
    if (input.value.startsWith('/')) showCmdMenu(input.value.trim());
    else hideCmdMenu();
  });
  input.addEventListener('blur', () => setTimeout(hideCmdMenu, 150));
  input.addEventListener('keydown', e => {
    if (e.key === 'Escape') hideCmdMenu();
  });
  form.addEventListener('submit', e => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) return;
    if (text.startsWith('/')) {
      const match = COMMANDS.find(c => c.cmd === text.split(/\s+/)[0].toLowerCase());
      if (match) { runCommand(match); return; }
    }
    sendCmd(text);
  });
  if (!loadHistory()) {
    addMsg('Kibo', 'agent', 'Ready. Tell me what to do on this PC \u2014 type <code>/</code> for the command list.');
  }
  loadModel();
});
