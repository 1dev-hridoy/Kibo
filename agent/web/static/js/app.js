let liveInterval = null;

function refreshScreen() {
  const img = document.getElementById('live-screen');
  img.src = '/api/screenshot?t=' + Date.now();
}

function toggleLiveView() {
  const btn = document.getElementById('live-btn');
  if (liveInterval) {
    clearInterval(liveInterval);
    liveInterval = null;
    btn.innerHTML = '<i class="bi bi-play"></i> Start live view';
  } else {
    liveInterval = setInterval(refreshScreen, 2000);
    btn.innerHTML = '<i class="bi bi-stop"></i> Stop live view';
    refreshScreen();
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const macroDialog = document.getElementById('macro-dialog');
  if (macroDialog) macroDialog.addEventListener('toggle', loadMacros);
  setVoiceBtn(true);
});
