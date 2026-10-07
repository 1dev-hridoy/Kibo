async function loadMacros() {
    const list = document.getElementById("macro-list");
    list.innerHTML = '<span class="text-muted small">Loading...</span>';
    try {
        const res = await fetch("/api/macros");
        const data = await res.json();
        if (!data.macros || !data.macros.length) {
            list.innerHTML = '<span class="text-muted small">No macros saved</span>';
            return;
        }
        list.innerHTML = "";
        data.macros.forEach(m => {
            const btn = document.createElement("button");
            btn.className = "btn btn-sm btn-outline-primary w-100 text-start mb-1";
            btn.innerHTML =
                '<i class="bi bi-play-circle"></i> ' +
                esc(m.name) +
                ' <span class="text-muted">' +
                m.steps +
                " steps</span>";
            btn.onclick = () => replayMacro(m.name);
            list.appendChild(btn);
        });
    } catch (e) {
        list.innerHTML = '<span class="text-danger small">Error loading macros</span>';
    }
}

async function startMacroRec() {
    const name = document.getElementById("macro-name").value.trim();
    if (!name) {
        alert("Enter a macro name");
        return;
    }
    await fetch("/api/macros/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name }),
    });
    addMsg("Kibo", "agent", "Recording macro: " + esc(name));
}

async function stopMacroRec() {
    await fetch("/api/macros/stop", { method: "POST" });
    addMsg("Kibo", "agent", "Macro recording stopped.");
    loadMacros();
}

async function replayMacro(name) {
    await fetch("/api/macros/replay", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name }),
    });
    addMsg("Kibo", "agent", "Replaying macro: " + esc(name));
}
