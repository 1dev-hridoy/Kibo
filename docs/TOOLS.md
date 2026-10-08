# Creating Tools for Kibo

Every capability in Kibo is a **tool**: a Python function decorated with
`@needle.tool`. The 14 MB model reads the name + docstring to decide when
to call it, so write both carefully.

## 1. Write the function

Create or open a module in `agent/tools/`, e.g. `agent/tools/my_tools.py`:

```python
import needle


@needle.tool
def greet_user(name: str = "friend") -> str:
    """Say hello to the user by name.
    Use when the user says hello, hi, or asks for a greeting."""
    print(f"[Tool] greet_user('{name}')")
    return f"Hello, {name}!"
```

Rules:

- **Name** is `snake_case`. The model sees `greet_user` as "greet user",
  plus an automatic `Also called: "greet user"` hint — pick names that
  sound like what users say.
- **Docstring** is the routing signal. First line says what it does,
  then a `Use when ...` line with example phrasings. This matters more
  than anything for the small model.
- **Arguments** need type hints (`str`, `int`, `float`, `bool`) and
  sensible defaults. Keep them few and simple.
- **Return a short string.** It becomes the agent's reply, the Telegram
  message, or the widget text.
- **Never import `agent.core` or `agent.tools` at top level** — circular
  imports. Lazy-import inside the function instead:

```python
@needle.tool
def my_tool() -> str:
    from agent.runner.something import helper
    return helper()
```

## 2. Register it

In `agent/tools/__init__.py`, import the function and add it to
`ALL_TOOLS`:

```python
from agent.tools.my_tools import greet_user

ALL_TOOLS = [
    ...
    greet_user,
]
```

Restart any running mode — tools load at startup. Count check:

```bash
python -c "from agent.tools import ALL_TOOLS; print(len(ALL_TOOLS))"
```

## 3. Skip the model with a fast-path (optional)

For commands the model keeps getting wrong, route deterministically in
`agent/core/fastpath.py` — it runs before the model in cli/web/telegram:

```python
if re.match(r"^say hello to (.+)$", t):
    return [("greet_user", {"name": m.group(1).strip()})]
```

Fast-paths also power the `/` menu and typo tolerance (`weight reset`
→ `widget_clear`, `breaf` → `brief_today`).

## 4. Heavy work goes in a runner (optional)

If the tool shells out, parses output, or manages state, put that logic
in `agent/runner/<name>.py` and keep the tool itself a thin wrapper:

```
agent/runner/my_feature.py   # logic, no needle import needed
agent/tools/my_tools.py      # @needle.tool wrappers
```

## 5. Test it

```bash
python -m unittest discover tests   # full suite
```

Then try the real phrasings in chat — including typos and short forms —
and watch the `[Tool]` log line to confirm the right function fired.
