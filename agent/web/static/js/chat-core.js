let currentReplyId = 0;

function esc(s) {
  const d = document.createElement('div');
  d.textContent = s == null ? '' : String(s);
  return d.innerHTML;
}

function addMsg(who, cls, html) {
  const wrap = document.getElementById('msgs');
  const div = document.createElement('div');
  div.className = 'msg ' + cls;
  const time = new Date().toLocaleTimeString();
  div.innerHTML = '<div class="who">' + esc(who) + ' \u00b7 ' + time + '</div><div class="bubble" data-role="bubble">' + html + '</div>';
  wrap.appendChild(div);
  wrap.scrollTop = wrap.scrollHeight;
  saveHistory();
  return div.querySelector('[data-role="bubble"]');
}

function clearChat() {
  const wrap = document.getElementById('msgs');
  wrap.innerHTML = '';
  localStorage.removeItem('kibo_chat_light');
  addMsg('Kibo', 'agent', 'Chat cleared. Ready.');
}

function saveHistory() {
  const wrap = document.getElementById('msgs');
  const items = [];
  wrap.querySelectorAll('.msg').forEach(m => {
    const who = m.querySelector('.who')?.textContent || '';
    const bubble = m.querySelector('[data-role="bubble"]')?.innerHTML || '';
    items.push({ who, bubble, cls: m.className });
  });
  try { localStorage.setItem('kibo_chat_light', JSON.stringify(items)); } catch (e) {}
}

function loadHistory() {
  try {
    const raw = localStorage.getItem('kibo_chat_light');
    if (!raw) return false;
    const items = JSON.parse(raw);
    const wrap = document.getElementById('msgs');
    wrap.innerHTML = '';
    items.forEach(m => {
      const div = document.createElement('div');
      div.className = m.cls;
      div.innerHTML = '<div class="who">' + m.who + '</div><div class="bubble" data-role="bubble">' + m.bubble + '</div>';
      wrap.appendChild(div);
    });
    wrap.scrollTop = wrap.scrollHeight;
    return true;
  } catch (e) { return false; }
}
