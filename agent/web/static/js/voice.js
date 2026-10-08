let voiceActive = false;
let voiceRecognition = null;
let voiceMode = 'unsupported';

(function detectVoiceMode() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SR && (location.protocol === 'https:' || location.hostname === 'localhost' || location.hostname === '127.0.0.1')) {
    voiceMode = 'webapi';
  } else if (location.protocol === 'http:' || location.protocol === 'https:') {
    voiceMode = 'vosk';
  }
})();

function setVoiceBtn(idle) {
  const btn = document.getElementById('voice-btn');
  if (!btn) return;
  btn.classList.toggle('btn-danger', !idle);
  btn.classList.toggle('btn-outline-secondary', idle);
  btn.innerHTML = idle ? '<i class="bi bi-mic"></i> Voice' : '<i class="bi bi-stop-circle"></i> Stop';
}

function toggleVoice() {
  if (voiceActive) stopVoice();
  else startVoice();
}

function startVoice() {
  voiceActive = true;
  if (voiceMode === 'webapi') startWebSpeech();
  else if (voiceMode === 'vosk') startVosk();
  else {
    addMsg('Kibo', 'agent', 'Voice needs Chrome/Edge over HTTPS or localhost.');
    voiceActive = false;
  }
}

function stopVoice() {
  voiceActive = false;
  if (voiceRecognition) { voiceRecognition.stop(); voiceRecognition = null; }
  setVoiceBtn(true);
}

function startWebSpeech() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  voiceRecognition = new SR();
  voiceRecognition.continuous = true;
  voiceRecognition.interimResults = true;
  voiceRecognition.lang = 'en-US';
  voiceRecognition.onresult = event => {
    let finalText = '';
    for (let i = event.resultIndex; i < event.results.length; i++) {
      if (event.results[i].isFinal) finalText += event.results[i][0].transcript;
    }
    if (finalText) sendChat(finalText.trim());
  };
  voiceRecognition.onerror = e => {
    if (e.error !== 'no-speech') console.warn('Voice error:', e.error);
  };
  voiceRecognition.onend = () => { if (voiceActive) voiceRecognition.start(); };
  voiceRecognition.start();
  setVoiceBtn(false);
  addMsg('Kibo', 'agent', '<i class="bi bi-mic"></i> Listening \u2014 speak your command.');
}

async function startVosk() {
  addMsg('Kibo', 'agent', '<i class="bi bi-mic"></i> Listening via server mic (10s)...');
  setVoiceBtn(false);
  try {
    const res = await fetch('/api/voice/listen', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ duration: 10 })
    });
    const data = await res.json();
    if (data.heard) addMsg('You', 'user', esc(data.heard));
    addMsg('Kibo', 'agent', esc(data.response || 'No speech detected.'));
  } catch (err) {
    addMsg('Kibo', 'agent', 'Voice error: ' + esc(err.message));
  }
  voiceActive = false;
  setVoiceBtn(true);
}
