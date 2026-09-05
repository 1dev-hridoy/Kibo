"""
Interactive CLI for Kibo.
"""

import sys
from .logs import user_input as log_user_input, ai_response as log_ai_response, info, error


def start_cli():
    """Start the interactive CLI."""
    from .core import ask

    print("\n" + "=" * 50)
    print("  Kibo — Your PC, controlled by chat")
    print("=" * 50)
    print("  Type 'help' for commands, 'quit' to exit\n")

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
            print(f"\nKibo: {response}\n")
            log_ai_response("cli", response, result.get("tool_calls"), result.get("results"))
        except Exception as e:
            error("cli", str(e))


if __name__ == "__main__":
    start_cli()
