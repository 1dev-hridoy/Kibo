"""
Model manager — handles Needle and FunctionGemma models.
Provides loading, switching, and a unified interface.
"""

import json
import os
import threading
import time

from agent.config import HOME

# Model paths
NEEDLE_MARKER = os.path.join(HOME, ".agent_model")
FUNCTIONGEMMA_DIR = os.path.join(HOME, ".agent_models", "functiongemma")
FUNCTIONGEMMA_MODEL = os.path.join(FUNCTIONGEMMA_DIR, "functiongemma-270m-it-Q4_K_M.gguf")
FUNCTIONGEMMA_REPO = "unsloth/functiongemma-270m-it-GGUF"
FUNCTIONGEMMA_FILE = "functiongemma-270m-it-Q4_K_M.gguf"
FUNCTIONGEMMA_URL = f"https://huggingface.co/{FUNCTIONGEMMA_REPO}/resolve/main/{FUNCTIONGEMMA_FILE}"

MODEL_CONFIG = os.path.join(HOME, ".agent_model_config.json")

# Model aliases — easy names users can type
MODEL_ALIASES = {
    "needle": "needle", "needle2": "needle", "needle 2": "needle",
    "n": "needle",
    "gemma": "functiongemma", "functiongemma": "functiongemma",
    "google": "functiongemma", "func": "functiongemma", "fg": "functiongemma",
    "functiongemma270m": "functiongemma", "functiongemma-270m": "functiongemma",
}

# Model metadata
MODELS = {
    "needle": {
        "name": "Needle 2",
        "maker": "Cactus Compute",
        "params": "45M",
        "size": "14 MB",
        "ram": "~28 MB",
        "speed": "1200 tok/s decode",
        "description": "Ultra-lightweight tool-calling model. Best for fast, low-resource PCs.",
        "strengths": [
            "Smallest model (14MB)",
            "Runs in 28MB RAM",
            "Built-in confidence scoring",
            "Tool retrieval for large toolsets",
            "Optimized for edge devices",
        ],
        "weaknesses": [
            "Limited general knowledge",
            "Smaller context window (256 tokens)",
            "Trained on fewer domains",
        ],
    },
    "functiongemma": {
        "name": "FunctionGemma 270M",
        "maker": "Google DeepMind",
        "params": "270M",
        "size": "~253 MB (Q4_K_M)",
        "ram": "~400 MB",
        "speed": "~50 tok/s decode",
        "description": "Google's specialized function-calling model. Better reasoning and tool use.",
        "strengths": [
            "Better reasoning than Needle",
            "256K vocabulary for rich JSON",
            "Strong function-calling accuracy",
            "Google Gemma architecture",
            "Wider tool support",
        ],
        "weaknesses": [
            "18x larger than Needle",
            "Requires more RAM (~400MB)",
            "Slower inference",
        ],
    },
}


def _load_config():
    """Load model configuration."""
    if os.path.exists(MODEL_CONFIG):
        with open(MODEL_CONFIG) as f:
            return json.load(f)
    return {"active_model": "needle"}


def _save_config(cfg):
    """Save model configuration."""
    with open(MODEL_CONFIG, "w") as f:
        json.dump(cfg, f, indent=2)


def get_active_model():
    """Get the currently active model name."""
    cfg = _load_config()
    return cfg.get("active_model", "needle")


def set_active_model(name):
    """Set the active model."""
    if name not in MODELS:
        raise ValueError(f"Unknown model: {name}. Available: {', '.join(MODELS)}")
    cfg = _load_config()
    cfg["active_model"] = name
    _save_config(cfg)
    return name


def is_model_available(name):
    """Check if a model is downloaded and available."""
    if name == "needle":
        return os.path.exists(NEEDLE_MARKER) or _needle_installed()
    elif name == "functiongemma":
        return os.path.exists(FUNCTIONGEMMA_MODEL)
    return False


def _needle_installed():
    """Check if Needle is installed via pip."""
    try:
        import needle
        return True
    except ImportError:
        return False


def get_model_status():
    """Get status of all models."""
    status = {}
    for name, info in MODELS.items():
        status[name] = {
            **info,
            "available": is_model_available(name),
            "active": name == get_active_model(),
        }
    return status


def resolve_model_name(name):
    """Resolve user input to a model name. Handles aliases."""
    name = name.lower().strip()
    return MODEL_ALIASES.get(name, name)


def switch_model(name):
    """Switch to a different model. Returns (success, message)."""
    name = resolve_model_name(name)

    if name not in MODELS:
        return False, (
            f"Unknown model: '{name}'.\n"
            f"Available: needle (14MB), functiongemma/gemma (253MB)\n"
            f"Type 'models' to see details."
        )

    old_model = get_active_model()
    if name == old_model:
        return True, f"Already using {MODELS[name]['name']}."

    if not is_model_available(name):
        return False, (
            f"Model '{MODELS[name]['name']}' is not downloaded.\n"
            f"Run: ./install.sh --fresh to download it."
        )

    set_active_model(name)
    return True, (
        f"Switched from {MODELS[old_model]['name']} to {MODELS[name]['name']}.\n"
        f"Restart required: type 'switch {name}' again or restart the bot."
    )


def get_models_display():
    """Get a formatted display of all models with info."""
    active = get_active_model()
    lines = []
    lines.append("=" * 50)
    lines.append("  Available Models")
    lines.append("=" * 50)
    for key, info in MODELS.items():
        marker = " <-- ACTIVE" if key == active else ""
        avail = "Ready" if is_model_available(key) else "Not downloaded"
        lines.append(f"\n  [{key.upper()}]{marker}")
        lines.append(f"  Name:     {info['name']}")
        lines.append(f"  Maker:    {info['maker']}")
        lines.append(f"  Params:   {info['params']}")
        lines.append(f"  Size:     {info['size']}")
        lines.append(f"  RAM:      {info['ram']}")
        lines.append(f"  Speed:    {info['speed']}")
        lines.append(f"  Status:   {avail}")
        lines.append(f"  {info['description']}")
        lines.append(f"  Strengths:")
        for s in info["strengths"]:
            lines.append(f"    + {s}")
    lines.append("")
    lines.append("  Quick switch:")
    lines.append("    needle / n    > Switch to Needle 2")
    lines.append("    gemma / fg    > Switch to FunctionGemma")
    lines.append("    models        > Show this list")
    lines.append("=" * 50)
    return "\n".join(lines)


class NeedleBackend:
    """Wrapper around cactus-needle."""

    def __init__(self, tools):
        import needle
        print("[Model] Loading Needle 2 (14MB)...")
        t0 = time.time()
        self.agent = needle.Needle(tools=tools)
        print(f"[Model] Needle loaded in {time.time() - t0:.1f}s")

    def reset(self):
        self.agent.reset()

    def complete(self, text):
        return self.agent._complete(text)


class FunctionGemmaBackend:
    """Wrapper around FunctionGemma via llama-cpp-python."""

    def __init__(self, tools):
        if not os.path.exists(FUNCTIONGEMMA_MODEL):
            raise FileNotFoundError(
                f"FunctionGemma model not found at {FUNCTIONGEMMA_MODEL}. "
                "Run install.sh to download it."
            )
        print("[Model] Loading FunctionGemma 270M...")
        t0 = time.time()
        try:
            from llama_cpp import Llama
        except ImportError:
            raise ImportError(
                "llama-cpp-python is required for FunctionGemma.\n"
                "Install it: pip install llama-cpp-python"
            )
        self.llm = Llama(
            model_path=FUNCTIONGEMMA_MODEL,
            n_ctx=2048,
            n_threads=max(1, os.cpu_count() - 1),
            verbose=False,
        )
        self.tools = {fn.__name__: fn for fn in tools}
        self.tool_schemas = self._build_tool_schemas(tools)
        print(f"[Model] FunctionGemma loaded in {time.time() - t0:.1f}s")

    def _build_tool_schemas(self, tools):
        """Build tool schema descriptions for FunctionGemma."""
        schemas = []
        for fn in tools:
            name = fn.__name__
            doc = (fn.__doc__ or "").strip().split("\n")[0]
            schemas.append(f"- {name}: {doc}")
        return "\n".join(schemas)

    def reset(self):
        pass

    def complete(self, text):
        """Complete using FunctionGemma with function calling format."""
        prompt = self._build_prompt(text)
        output = self.llm(
            prompt,
            max_tokens=256,
            temperature=0.1,
            stop=["<end_of_turn>"],
        )
        raw = output["choices"][0]["text"].strip()
        return self._parse_response(raw)

    def _build_prompt(self, user_text):
        """Build FunctionGemma prompt with tool definitions."""
        return (
            f"<start_of_turn>user\n"
            f"You are a function calling AI assistant.\n"
            f"You have access to these tools:\n{self.tool_schemas}\n\n"
            f"To call a tool, respond with a JSON object:\n"
            f'{{"type": "call", "function_calls": [{{"name": "tool_name", "arguments": {{}}}}]}}\n\n'
            f"If no tool is needed, respond with natural text.\n\n"
            f"{user_text}<end_of_turn>\n"
            f"<start_of_turn>model\n"
        )

    def _parse_response(self, raw):
        """Parse FunctionGemma response into standard format."""
        try:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start >= 0 and end > start:
                data = json.loads(raw[start:end])
                if "function_calls" in data:
                    return {
                        "type": "call",
                        "function_calls": data["function_calls"],
                        "confidence": 0.8,
                        "reasoning": "",
                    }
        except (json.JSONDecodeError, ValueError):
            pass
        return {
            "type": "text",
            "function_calls": [],
            "confidence": 0.0,
            "reasoning": raw,
        }


def create_backend(tools):
    """Create the appropriate backend based on active model."""
    model = get_active_model()
    if model == "functiongemma":
        return FunctionGemmaBackend(tools)
    return NeedleBackend(tools)
