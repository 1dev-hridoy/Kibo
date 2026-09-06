"""
Flask web server — provides the water.css chat UI and REST API.
"""

import os
import sys
import json
import secrets

from flask import Flask, request, jsonify, render_template_string, send_file, session, redirect, url_for
from flask_socketio import SocketIO, emit
from agent.core import ask
from agent.config import WEB_HOST, WEB_PORT
from agent.tools import ALL_TOOLS
from agent.logs import user_input, ai_response, error, startup

app = Flask(__name__)
app.secret_key = os.urandom(24)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

_template_dir = os.path.dirname(os.path.abspath(__file__))
_template_path = os.path.join(_template_dir, "template.html")
with open(_template_path) as _f:
    HTML_TEMPLATE = _f.read()


def _check_auth():
    """Check if user is authenticated."""
    from .auth import is_auth_required, verify_token
    if not is_auth_required():
        return True
    token = session.get("token") or request.headers.get("X-Auth-Token")
    return verify_token(token)


LOGIN_HTML = """<!DOCTYPE html>
<html><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Kibo Login</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/water.css@2/out/water.min.css">
<style>body{max-width:400px;margin:10vh auto;text-align:center}</style>
</head><body>
<h1>Kibo</h1>
<form method="POST" action="/login">
  <input type="password" name="password" placeholder="Enter password" required autofocus
         style="width:100%;padding:12px;font-size:16px;margin:8px 0;box-sizing:border-box">
  <button type="submit" style="width:100%;padding:12px;font-size:16px">Unlock</button>
</form>
</body></html>"""


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password", "")
        from .auth import verify_password, generate_token
        if verify_password(password):
            token = generate_token()
            session["token"] = token
            return redirect(url_for("index"))
        return "Invalid password", 401
    return render_template_string(LOGIN_HTML)


@app.route("/api/auth/setup", methods=["POST"])
def setup_auth():
    """Set or change password."""
    data = request.get_json(force=True)
    password = data.get("password", "")
    if len(password) < 4:
        return jsonify({"error": "Password must be at least 4 characters"}), 400
    from .auth import setup_password
    setup_password(password)
    return jsonify({"success": True, "message": "Password set"})


@app.route("/api/auth/remove", methods=["POST"])
def remove_auth():
    """Remove password protection."""
    from .auth import remove_password
    remove_password()
    return jsonify({"success": True})


@app.route("/")
def index():
    if not _check_auth():
        return redirect(url_for("login"))
    return render_template_string(HTML_TEMPLATE)@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.get_json(force=True) if request.is_json else request.form
        password = data.get("password", "")
        from .auth import verify_password, generate_token
        if verify_password(password):
            token = generate_token()
            session["token"] = token
            if request.is_json:
                return jsonify({"success": True, "token": token})
            return redirect(url_for("index"))
        if request.is_json:
            return jsonify({"success": False, "error": "Invalid password"}), 401
        return "Invalid password", 401
    return render_template_string(LOGIN_HTML)


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    user_msg = data.get("message", "").strip()
    if not user_msg:
        return jsonify({"error": "Empty message"}), 400

    user_input("web", user_msg)

    try:
        result = ask(user_msg)
        calls = result.get("tool_calls") or []
        media = result.get("media")
        text = result.get("text", "")

        ai_response("web", text, calls, result.get("results"))

        response = {
            "response": text,
            "tools": [c["name"] for c in calls],
            "results": [str(r) for r in (result.get("results") or [])],
        }
        if media and media.get("path") and os.path.exists(media["path"]):
            response["media"] = {
                "type": media["type"],
                "url": f"/api/media?path={media['path']}",
            }
        return jsonify(response)
    except Exception as e:
        error("web", str(e))
        return jsonify({"error": str(e)}), 500


@app.route("/api/media")
def serve_media():
    """Serve a media file (screenshot/photo) by path."""
    path = request.args.get("path", "")
    if not path or not os.path.exists(path):
        return "Not found", 404
    abs_path = os.path.abspath(path)
    allowed = [os.path.expanduser("~/Downloads"), os.path.expanduser("~")]
    if not any(abs_path.startswith(d) for d in allowed):
        return "Forbidden", 403
    return send_file(abs_path)


@app.route("/api/tools")
def list_tools():
    """Return the list of registered tool names."""
    names = [t.__name__ for t in ALL_TOOLS]
    return jsonify({"tools": names})


@app.route("/api/model", methods=["GET"])
def get_model():
    """Get current model info."""
    from agent.model_manager import get_active_model, MODELS
    current = get_active_model()
    info = MODELS.get(current, {})
    return jsonify({
        "active": current,
        "name": info.get("name", current),
        "maker": info.get("maker", ""),
        "size": info.get("size", ""),
    })


@app.route("/api/model", methods=["POST"])
def set_model():
    """Switch model."""
    data = request.get_json(force=True)
    model = data.get("model", "").strip().lower()
    if not model:
        return jsonify({"error": "No model specified"}), 400

    from agent.model_manager import switch_model, MODELS
    from agent.core.engine import reload_backend

    success, msg = switch_model(model)
    if success:
        reload_backend()
    return jsonify({"success": success, "message": msg})


@app.route("/api/models")
def list_models():
    """List all available models."""
    from agent.model_manager import get_active_model, get_models_list
    current = get_active_model()
    models = get_models_list()
    return jsonify({"current": current, "models": models})


@app.route("/api/history")
def get_history():
    """Get conversation history."""
    from agent.core.context import _history, _tool_history
    return jsonify({
        "history": list(_history),
        "tools": list(_tool_history),
    })


@app.route("/api/history", methods=["DELETE"])
def clear_history():
    """Clear conversation history."""
    from agent.core.context import clear_context
    clear_context()
    return jsonify({"success": True})


@app.route("/api/screenshot")
def live_screenshot():
    """Get a fresh screenshot for live viewing."""
    from .live_view import get_latest_screenshot
    path = get_latest_screenshot(force=True)
    if path and os.path.exists(path):
        return send_file(path, mimetype="image/png")
    return "Screenshot failed", 500


@app.route("/api/screen-info")
def screen_info():
    """Get screen resolution info."""
    from .live_view import get_screen_info
    return jsonify({"info": get_screen_info()})



_terminal_sessions = {}


@socketio.on("terminal:create")
def handle_terminal_create(data):
    """Create a new terminal session."""
    from .terminal import create_session
    cols = data.get("cols", 80)
    rows = data.get("rows", 24)
    session_id, msg = create_session(cols=cols, rows=rows)
    _terminal_sessions[request.sid] = session_id
    emit("terminal:created", {"session_id": session_id, "message": msg})


@socketio.on("terminal:input")
def handle_terminal_input(data):
    """Handle terminal input."""
    from .terminal import write_to_session
    session_id = _terminal_sessions.get(request.sid)
    if session_id:
        write_to_session(session_id, data.get("input", ""))
  
        output = ""
        while True:
            chunk = read_from_session(session_id)
            if not chunk:
                break
            output += chunk
        if output:
            emit("terminal:output", {"output": output})


@socketio.on("terminal:resize")
def handle_terminal_resize(data):
    """Resize terminal."""
    from .terminal import resize_session
    session_id = _terminal_sessions.get(request.sid)
    if session_id:
        resize_session(session_id, data.get("cols", 80), data.get("rows", 24))


@socketio.on("terminal:close")
def handle_terminal_close():
    """Close terminal session."""
    from .terminal import close_session
    session_id = _terminal_sessions.pop(request.sid, None)
    if session_id:
        close_session(session_id)


@socketio.on("disconnect")
def handle_disconnect():
    """Clean up on disconnect."""
    from .terminal import close_session
    session_id = _terminal_sessions.pop(request.sid, None)
    if session_id:
        close_session(session_id)


def read_from_session(session_id):
    """Read from terminal session."""
    from .terminal import read_from_session as _read
    return _read(session_id)






@app.route("/api/macros")
def get_macros():
    """List all macros."""
    from agent.core.macros import list_macros, _ensure_dir, MACROS_DIR
    import os
    _ensure_dir()
    macros = []
    for f in os.listdir(MACROS_DIR):
        if f.endswith(".json"):
            path = os.path.join(MACROS_DIR, f)
            try:
                with open(path) as fh:
                    m = json.load(fh)
                    macros.append({
                        "name": m.get("name", f[:-5]),
                        "steps": m.get("step_count", len(m.get("steps", []))),
                    })
            except Exception:
                pass
    return jsonify({"macros": macros})


@app.route("/api/macros/start", methods=["POST"])
def start_macro():
    """Start recording a macro."""
    from agent.core.macros import start_recording
    data = request.get_json(force=True)
    name = data.get("name", "unnamed")
    result = start_recording(name)
    return jsonify({"success": True, "message": result})


@app.route("/api/macros/stop", methods=["POST"])
def stop_macro():
    """Stop recording."""
    from agent.core.macros import stop_recording
    result = stop_recording()
    return jsonify({"success": True, "message": result})


@app.route("/api/macros/replay", methods=["POST"])
def replay_macro_api():
    """Replay a macro."""
    from agent.core.macros import replay_macro
    data = request.get_json(force=True)
    name = data.get("name", "")
    result = replay_macro(name)
    return jsonify({"success": True, "message": result})


def start_web(host: str = WEB_HOST, port: int = WEB_PORT):
    """Start the web server with WebSocket support."""
    startup("Web", f"http://{host}:{port}")
    print(f"Kibo Web UI: http://{host}:{port}")
    socketio.run(app, host=host, port=port, debug=False, allow_unsafe_werkzeug=True)
