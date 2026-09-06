"""
Interactive CLI for Kibo.
Supports screenshot preview via chafa/viu, tool call display, and command history.
"""

import sys
import os
import shutil
from .logs import user_input as log_user_input, ai_response as log_ai_response, info, error


def _find_image_viewer():
    """Find available terminal image viewer."""
    for viewer in ["chafa", "viu", "timg", "imgcat"]:
        if shutil.which(viewer):
            return viewer
    return None


def _show_image(path, viewer=None):
    """Display an image in the terminal."""
    if viewer is None:
        viewer = _find_image_viewer()
    if viewer is None:
        print(f"  [Image saved: {path}]")
        return

    try:
        if viewer == "chafa":
            os.system(f'chafa --size=40x20 "{path}" 2>/dev/null')
        elif viewer == "viu":
            os.system(f'viu -w 60 "{path}" 2>/dev/null')
        elif viewer == "timg":
            os.system(f'timg -g 60x20 "{path}" 2>/dev/null')
        elif viewer == "imgcat":
            os.system(f'imgcat --width=60 "{path}" 2>/dev/null')
        else:
            print(f"  [Image saved: {path}]")
    except Exception:
        print(f"  [Image saved: {path}]")


def _format_tool_calls(calls, results=None):
    """Format tool calls for display."""
    if not calls:
        return ""
    lines = []
    for i, c in enumerate(calls):
        name = c.get("name", "?")
        args = c.get("arguments", {})
        args_str = ", ".join(f"{k}={v!r}" for k, v in args.items()) if args else ""
        result = results[i] if results and i < len(results) else ""
        lines.append(f"  → {name}({args_str})")
        if result:
            result_str = str(result)[:150]
            lines.append(f"  ← {result_str}")
    return "\n".join(lines)


def start_cli():
    """Start the interactive CLI."""
    from .core import ask

    viewer = _find_image_viewer()
    viewer_name = f" ({viewer})" if viewer else " (no image viewer)"

    print("\n" + "=" * 50)
    print("  Kibo — Your PC, controlled by chat")
    print("=" * 50)
    print(f"  Type 'help' for commands, 'quit' to exit")
    print(f"  Image preview: {viewer_name}")
    print()

    while True:
        try:
            user_msg = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not user_msg:
            continue

        if user_msg.lower() in ("quit", "exit", "q"):
            print("Bye!")
            break

        log_user_input("cli", user_msg)

        try:
            result = ask(user_msg)
            response = result.get("text", "")
            media = result.get("media")
            tool_calls = result.get("tool_calls", [])
            results = result.get("results", [])

       
            print(f"\nKibo: {response}")

        
            if tool_calls:
                tools_display = _format_tool_calls(tool_calls, results)
                if tools_display:
                    print(tools_display)

         
            if media and media.get("path") and os.path.exists(media["path"]):
                _show_image(media["path"], viewer)

            print()
            log_ai_response("cli", response, tool_calls, results)
        except Exception as e:
            error("cli", str(e))


if __name__ == "__main__":
    start_cli()
