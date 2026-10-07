let termSocket = null;
let termConnected = false;

function openTerminal() {
    document.getElementById("terminal-dialog").showModal();
    if (!termConnected) connectTerminal();
}

function connectTerminal() {
    termSocket = io();
    termSocket.on("connect", () => {
        termConnected = true;
        termSocket.emit("terminal:create", { cols: 80, rows: 24 });
    });
    termSocket.on("terminal:created", d => addTerminalOutput("Terminal session: " + d.session_id + "\n"));
    termSocket.on("terminal:output", d => addTerminalOutput(d.output));
    termSocket.on("disconnect", () => {
        termConnected = false;
    });
}

function addTerminalOutput(text) {
    const box = document.getElementById("terminal-container");
    box.textContent += text;
    box.scrollTop = box.scrollHeight;
}

function sendTerminalInput() {
    const box = document.getElementById("terminal-input");
    const text = box.value;
    if (text && termSocket) {
        termSocket.emit("terminal:input", { input: text + "\n" });
        box.value = "";
    }
}
