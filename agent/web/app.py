"""
Flask web server — provides the water.css chat UI and REST API.
"""

import os
import sys
import json

from flask import Flask, request, jsonify, render_template_string, send_file
from agent.core import ask
from agent.config import WEB_HOST, WEB_PORT
from agent.tools import ALL_TOOLS
from agent.logs import user_input, ai_response, error, startup

app = Flask(__name__)

_template_dir = os.path.dirname(os.path.abspath(__file__))
_template_path = os.path.join(_template_dir, "template.html")
with open(_template_path) as _f:
    HTML_TEMPLATE = _f.read()


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


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


def start_web(host: str = WEB_HOST, port: int = WEB_PORT):
    """Start the web server."""
    startup("Web", f"http://{host}:{port}")
    print(f"Kibo Web UI: http://{host}:{port}")
    try:
        from waitress import serve
        serve(app, host=host, port=port)
    except ImportError:
        app.run(host=host, port=port, debug=False)
