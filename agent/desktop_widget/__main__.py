"""Entry point for the desktop widget: `python -m agent.desktop_widget`"""

import os


def main():
    if os.name == "posix" and "DISPLAY" not in os.environ:
        os.environ["DISPLAY"] = ":0"
    from agent.desktop_widget.widget import KiboWidget
    KiboWidget().run()


if __name__ == "__main__":
    main()