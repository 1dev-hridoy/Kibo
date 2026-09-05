"""
Interactive CLI for Kibo.
"""

import sys
from .logs import log_user_input, log_ai_response


def start_cli():
    """Start the interactive CLI."""
    from .core import ask

    print("\n" + "=" * 50)
    print("  Kibo — Your PC, controlled by chat")
    print("=" * 50)
    print("  Type 'help' for commands, 'quit' to exit\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "q"):
            print("Bye!")
            break

        log_user_input(user_input)

        try:
            result = ask(user_input)
            response = result.get("text", "")
            print(f"\nKibo: {response}\n")
            log_ai_response(response)
        except Exception as e:
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    start_cli()
