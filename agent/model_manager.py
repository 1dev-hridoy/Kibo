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
_MODELS_DIR = os.path.join(HOME, ".agent_models")

# llama.cpp (GGUF) model registry: repo + file + prompt family.
# "gemma" → <start_of_turn> markers, "chatml" → <|im_start|> markers.
GGUF_MODELS = {
    "functiongemma": {
        "repo": "unsloth/functiongemma-270m-it-GGUF",
        "file": "functiongemma-270m-it-Q4_K_M.gguf",
        "family": "gemma",
        "n_ctx": 2048,
    },
    "qwen3-0.6b": {
        "repo": "unsloth/Qwen3-0.6B-GGUF",
        "file": "Qwen3-0.6B-Q4_K_M.gguf",
        "family": "chatml",
        "n_ctx": 4096,
    },
    "qwen2.5-1.5b": {
        "repo": "Qwen/Qwen2.5-1.5B-Instruct-GGUF",
        "file": "qwen2.5-1.5b-instruct-q4_k_m.gguf",
        "family": "chatml",
        "n_ctx": 4096,
    },
    "qwen2.5-3b": {
        "repo": "Qwen/Qwen2.5-3B-Instruct-GGUF",
        "file": "qwen2.5-3b-instruct-q4_k_m.gguf",
        "family": "chatml",
        "n_ctx": 4096,
    },
    "gemma3-1b": {
        "repo": "unsloth/gemma-3-1b-it-GGUF",
        "file": "gemma-3-1b-it-Q4_K_M.gguf",
        "family": "gemma",
        "n_ctx": 4096,
    },
    "gemma3-4b": {
        "repo": "unsloth/gemma-3-4b-it-GGUF",
        "file": "gemma-3-4b-it-Q4_K_M.gguf",
        "family": "gemma",
        "n_ctx": 4096,
    },
}


def model_path(name):
    """Absolute path to a GGUF model file, or None for known names."""
    info = GGUF_MODELS.get(name)
    if not info:
        return None
    return os.path.join(_MODELS_DIR, name, info["file"])


def model_url(name):
    """Hugging Face download URL for a GGUF model, or None."""
    info = GGUF_MODELS.get(name)
    if not info:
        return None
    return f"https://huggingface.co/{info['repo']}/resolve/main/{info['file']}"


# Backwards-compatible FunctionGemma constants
FUNCTIONGEMMA_DIR = os.path.join(_MODELS_DIR, "functiongemma")
FUNCTIONGEMMA_MODEL = model_path("functiongemma")
FUNCTIONGEMMA_REPO = GGUF_MODELS["functiongemma"]["repo"]
FUNCTIONGEMMA_FILE = GGUF_MODELS["functiongemma"]["file"]
FUNCTIONGEMMA_URL = model_url("functiongemma")

MODEL_CONFIG = os.path.join(HOME, ".agent_model_config.json")

# Model aliases — easy names users can type
MODEL_ALIASES = {
    "needle": "needle", "needle2": "needle", "needle 2": "needle",
    "n": "needle",
    "gemma": "functiongemma", "functiongemma": "functiongemma",
    "google": "functiongemma", "func": "functiongemma", "fg": "functiongemma",
    "functiongemma270m": "functiongemma", "functiongemma-270m": "functiongemma",
    # Qwen3 0.6B
    "qwen": "qwen3-0.6b", "qwen3": "qwen3-0.6b",
    "qwen3-0.6b": "qwen3-0.6b", "qwen-0.6b": "qwen3-0.6b",
    "qwen3-0.6": "qwen3-0.6b", "qwen0.6b": "qwen3-0.6b",
    # Qwen2.5 1.5B
    "qwen2.5-1.5b": "qwen2.5-1.5b", "qwen2.5-1.5": "qwen2.5-1.5b",
    "qwen1.5b": "qwen2.5-1.5b", "qwen-1.5b": "qwen2.5-1.5b",
    # Qwen2.5 3B
    "qwen2.5-3b": "qwen2.5-3b", "qwen2.5-3": "qwen2.5-3b",
    "qwen3b": "qwen2.5-3b", "qwen-3b": "qwen2.5-3b",
    # Gemma 3 1B
    "gemma3": "gemma3-1b", "gemma3-1b": "gemma3-1b",
    "gemma-3-1b": "gemma3-1b", "gemma-1b": "gemma3-1b", "g3-1b": "gemma3-1b",
    # Gemma 3 4B
    "gemma3-4b": "gemma3-4b", "gemma-3-4b": "gemma3-4b",
    "gemma-4b": "gemma3-4b", "g3-4b": "gemma3-4b",
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
        "license": "Apache-2.0 (Needle)",
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
        "license": "Gemma Terms",
    },
    "qwen3-0.6b": {
        "name": "Qwen3 0.6B",
        "maker": "Alibaba/Qwen (unsloth)",
        "params": "0.6B",
        "size": "~397 MB (Q4_K_M)",
        "ram": "~600 MB",
        "speed": "~20–40 tok/s decode",
        "description": "Tiny general model with tool-calling; best if you want 32k context with small size.",


        "strengths": [
            "Apache-2.0, commercial-safe",
            "32k context",
            "Fast enough for most CPU setups",
            "Good tool-calling for its size",
        ],


        "weaknesses": [
            "Needs llama-cpp-python",
            "Heavier than FunctionGemma",
            "Can hallucinate without grammar constraints",
        ],
        "license": "Apache-2.0",
    },



    "qwen2.5-1.5b": {
        "name": "Qwen2.5 1.5B Instruct",
        "maker": "Alibaba/Qwen",
        "params": "1.5B",
        "size": "~1.12 GB (Q4_K_M)",
        "ram": "~1.4 GB",
        "speed": "~15–25 tok/s decode",
        "description": "Solid all-round model with strong instruction-following and tool-calling.",
    
    
        "strengths": [
            "Apache-2.0, commercial-safe",
            "32k context",
            "Reliable instruction-following",
        ],
        "weaknesses": [
            "1GB+ download/ram",
            "Slower on weak CPUs",
        ],
        "license": "Apache-2.0",
    },



    "qwen2.5-3b": {
        "name": "Qwen2.5 3B Instruct",
        "maker": "Alibaba/Qwen",
        "params": "3B",
        "size": "~2.1 GB (Q4_K_M)",
        "ram": "~2.4 GB",
        "speed": "~10–18 tok/s decode",
        "description": "Most capable of the Qwen2.5 trio; runs fine on modern CPUs.",
        "strengths": [
            "Strong reasoning + tool use",
            "32k context",
        ],
        "weaknesses": [
            "Large download",
            "May be slow on older CPUs",
            "Qwen-Research license (non-commercial-like; check terms)",
        ],
        "license": "Qwen-Research",
    },




    "gemma3-1b": {
        "name": "Gemma 3 1B Instruct",
        "maker": "Google DeepMind (unsloth)",
        "params": "1B",
        "size": "~806 MB (Q4_K_M)",
        "ram": "~1 GB",
        "speed": "~15–25 tok/s decode",
        "description": "Gemma 3 text-only capable; good balance with 128k context in practice.",
        "strengths": [
            "128k context",
            "Compact for size class",
        ],
        "weaknesses": [
            "Gemma Terms (gated in some sources)",
            "May need HF token in some environments",
            "Tool-calling needs prompt/grammar discipline",
        ],
        "license": "Gemma Terms",
    },



    "gemma3-4b": {
        "name": "Gemma 3 4B Instruct",
        "maker": "Google DeepMind (unsloth)",
        "params": "4B",
        "size": "~2.49 GB (Q4_K_M)",
        "ram": "~3 GB",
        "speed": "~8–15 tok/s decode",
        "description": "Most capable of the added models; powerful but heavier on CPU.",
        "strengths": [
            "Strong reasoning",
            "128k context",
        ],
        "weaknesses": [
            "Gemma Terms (gated in some sources)",
            "~3GB RAM / 2.5GB download",
            "Slowest of the new set on CPU",
        ],
        "license": "Gemma Terms",
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
    path = model_path(name)
    return bool(path) and os.path.exists(path)


def download_model(name, progress=True):
    """Download a GGUF model. Returns (success, message)."""
    name = resolve_model_name(name)
    if name == "needle":
        return True, "Needle is installed via pip."
    info = GGUF_MODELS.get(name)
    if info is None:
        return False, f"Unknown model: '{name}'."
    dest = model_path(name)
    if os.path.exists(dest):
        return True, f"{MODELS.get(name, {}).get('name', name)} already downloaded."



    try:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
    except OSError as exc:
        return False, f"Could not create model directory: {exc}"

    url = model_url(name)
    label = MODELS.get(name, {}).get("name", name)
    size = MODELS.get(name, {}).get("size", "")
    tmp = dest + ".part"
    print(f"[Model] Downloading {label} {size} ...")



    try:
        import urllib.request
        req = urllib.request.Request(url, headers={"User-Agent": "kibo"})
        with urllib.request.urlopen(req, timeout=60) as resp, open(tmp, "wb") as fh:
            total = int(resp.headers.get("Content-Length") or 0)
            done = 0
            last_pct = -1
            while True:
                chunk = resp.read(1 << 20)
                if not chunk:
                    break
                fh.write(chunk)
                done += len(chunk)
                if progress and total:
                    pct = done * 100 // total
                    if pct >= last_pct + 5:
                        print(f"\r[Model] {pct}%", end="", flush=True)


                        last_pct = pct



        if progress:
            print()
        os.replace(tmp, dest)
        return True, f"{label} downloaded."
    except Exception as exc: 
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except OSError:
            pass
        msg = str(exc)
        if any(code in msg for code in ("401", "403", "Unauthorized", "Forbidden")):
            return False, (
                f"Could not download {label}: access denied. This model may be "
                "gated — accept its license on Hugging Face (and set HF_TOKEN)."
            )
        return False, f"Could not download {label}: {exc}"


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
            f"Available: needle (14MB), functiongemma/gemma (253MB), "
            f"qwen (397MB), qwen1.5b (1.1GB), qwen3b (2.1GB), "
            f"gemma3-1b (806MB), gemma3-4b (2.5GB)\n"
            f"Type 'models' to see details."
        )

    old_model = get_active_model()
    if name == old_model:
        return True, f"Already using {MODELS[name]['name']}."

    if not is_model_available(name):
        label = MODELS[name]['name']
        size = MODELS[name].get('size', '')
        print(f"[Model] {label} not found — downloading {size} ...")
        ok, dl_msg = download_model(name)
        print(f"[Model] {dl_msg}")
        if not ok:


            return False, (


                f"{label} is not downloaded and could not be fetched.\n{dl_msg}"
            )
        set_active_model(name)
        return True, (
            f"Downloaded {label}.\n"
            f"Switched from {MODELS[old_model]['name']} to {label}."
        )

    set_active_model(name)
    return True, (
        f"Switched from {MODELS[old_model]['name']} to {MODELS[name]['name']}."
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
        lines.append(f"  License:  {info.get('license', 'Unknown')}")
        lines.append(f"  Status:   {avail}")
        lines.append(f"  {info['description']}")
        lines.append(f"  Strengths:")
        for s in info["strengths"]:
            lines.append(f"    + {s}")
    lines.append("")
    lines.append("  Quick switch:")
    lines.append("    needle / n         > Needle 2")
    lines.append("    gemma / fg         > FunctionGemma")
    lines.append("    qwen               > Qwen3 0.6B")
    lines.append("    qwen1.5b           > Qwen2.5 1.5B")
    lines.append("    qwen3b             > Qwen2.5 3B")
    lines.append("    gemma3-1b          > Gemma 3 1B")
    lines.append("    gemma3-4b          > Gemma 3 4B")
    lines.append("    models             > Show this list")
    return "\n".join(lines)


def get_models_list():
    """Get a list of all models with their info."""
    active = get_active_model()
    models = []
    for key, info in MODELS.items():
        models.append({
            "key": key,
            "name": info["name"],
            "maker": info["maker"],
            "params": info["params"],
            "size": info["size"],
            "ram": info["ram"],
            "speed": info["speed"],
            "license": info.get("license", "Unknown"),
            "available": is_model_available(key),
            "active": key == active,
        })
    return models
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


class LlamaCppBackend:
    """Generic llama.cpp backend for GGUF instruction models.

    `family` selects the prompt turn markers and stop token:
      - "gemma"  → <start_of_turn> ... <end_of_turn>
      - "chatml" → <|im_start|> ... <|im_end|>  (Qwen family)
    """

    def __init__(self, model_path, family="chatml", n_ctx=4096, name=None):
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model not found at {model_path}. Download it first."
            )
        print(f"[Model] Loading {name or os.path.basename(model_path)}...")
        t0 = time.time()
        try:
            from llama_cpp import Llama
        except ImportError:
            raise ImportError(
                "llama-cpp-python is required for GGUF models.\n"
                "Install it: pip install llama-cpp-python"
            )
        self.llm = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_threads=max(1, os.cpu_count() - 1),
            verbose=False,
        )
        self.family = family
        self.name = name or os.path.basename(model_path)
        self.stop = ["<end_of_turn>"] if family == "gemma" else ["<|im_end|>"]
        self.tools = {}
        self.tool_schemas = ""
        print(f"[Model] {self.name} loaded in {time.time() - t0:.1f}s")

    def set_tools(self, tools):
        self.tools = {fn.__name__: fn for fn in tools}
        self.tool_schemas = self._build_tool_schemas(tools)

    def _build_tool_schemas(self, tools):
        """Build a compact tool-name + docstring list for the prompt."""
        schemas = []
        for fn in tools:
            name = fn.__name__
            doc = (fn.__doc__ or "").strip().split("\n")[0]
            schemas.append(f"- {name}: {doc}")
        return "\n".join(schemas)

    def reset(self):
        pass

    def _system_text(self):
    
        extra = "\n/no_think" if self.family == "chatml" else ""
        return (
            "You are Kibo, a function calling AI assistant.\n"
            f"You have access to these tools:\n{self.tool_schemas}\n\n"
            "To call a tool, respond with ONLY this JSON object:\n"
            '{"type": "call", "function_calls": '
            '[{"name": "tool_name", "arguments": {}}]}\n\n'
            "If no tool is needed, respond with ONLY this JSON object:\n"
            '{"type": "respond", "reasoning": "your reply"}'
            f"{extra}"
        )



    def _build_prompt(self, user_text):
        """Build a prompt using the model family's chat markers."""
        system = self._system_text()
        if self.family == "gemma":
            return (
                f"<start_of_turn>user\n{system}\n\n{user_text}<end_of_turn>\n"
                f"<start_of_turn>model\n"
            )

        
        return (
            f"<|im_start|>system\n{system}<|im_end|>\n"
            f"<|im_start|>user\n{user_text}<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )

    def complete(self, text):
        """Run the model and return the standard engine envelope."""
        prompt = self._build_prompt(text)
        output = self.llm(
            prompt,
            max_tokens=256,
            temperature=0.1,
            stop=self.stop,
        )
        raw = output["choices"][0]["text"].strip()
        return self._parse_response(raw)

    def _parse_response(self, raw):
        """Parse model output into the {"type","function_calls",...} envelope."""
        try:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start >= 0 and end > start:
                data = json.loads(raw[start:end])
                calls = data.get("function_calls")
                if calls:
                    return {
                        "type": "call",
                        "function_calls": calls,
                        "confidence": 0.8,
                        "reasoning": data.get("reasoning", ""),
                    }
                if data.get("reasoning"):
                    return {
                        "type": "respond",
                        "function_calls": [],
                        "confidence": 0.0,
                        "reasoning": data["reasoning"],
                    }
        except (json.JSONDecodeError, ValueError):
            pass
        return {
            "type": "text",
            "function_calls": [],
            "confidence": 0.0,
            "reasoning": raw,
        }


class FunctionGemmaBackend(LlamaCppBackend):
    """FunctionGemma via the generic llama.cpp backend (kept for compat)."""

    def __init__(self, tools):
        super().__init__(
            FUNCTIONGEMMA_MODEL, family="gemma", n_ctx=2048,
            name="FunctionGemma 270M",
        )
        self.set_tools(tools)


def create_backend(tools):
    """Create the appropriate backend based on the active model."""
    model = get_active_model()

    if model not in MODELS or model == "needle":
        if model not in MODELS:
            print(f"[Model] Unknown model '{model}', using Needle")
            set_active_model("needle")
        return NeedleBackend(tools)



    info = GGUF_MODELS.get(model)
    path = model_path(model)
    label = MODELS.get(model, {}).get("name", model)



    if not info or not path:
        print(f"[Model] No backend for '{model}', using Needle")
        set_active_model("needle")
        return NeedleBackend(tools)



    if not os.path.exists(path):
        print(f"[Model] {label} not found — downloading...")
        ok, msg = download_model(model)
        print(f"[Model] {msg}")
        if not ok or not os.path.exists(path):
            print("[Model] Falling back to Needle")
            set_active_model("needle")
            return NeedleBackend(tools)

    try:
        backend = LlamaCppBackend(
            path, family=info["family"], n_ctx=info["n_ctx"], name=label,
        )
        backend.set_tools(tools)
        return backend
    except ImportError:
        print("[Model] llama-cpp-python missing — install it: "
              "pip install llama-cpp-python")
        print("[Model] Falling back to Needle")
        set_active_model("needle")
        return NeedleBackend(tools)

