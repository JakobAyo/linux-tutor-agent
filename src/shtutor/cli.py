"""`shtutor` entry point. With no arguments it opens the lesson reader (ADR 0022)."""

from __future__ import annotations

import argparse
from importlib.metadata import version


def main() -> None:
    p = argparse.ArgumentParser(
        prog="shtutor",
        description="Read the lessons written from the commands you run.",
        epilog="Data directory: $LTUTOR_SPIKE_DIR, default ~/.local/share/linux-tutor-spike (M1).",
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {version('shtutor')}")
    p.parse_args()

    from shtutor.tui import ReaderApp  # import Textual only when the UI actually starts

    ReaderApp().run()


if __name__ == "__main__":
    main()
