"""DeepSeek Token Monitor - Desktop overlay for real-time token usage.

Reads token usage directly from CC-Switch's database.
No proxy needed - just install and run.

Usage:
  python main.py
"""
import sys

from overlay import TokenOverlay


def main():
    print("  DeepSeek Token Monitor")
    print("  Reading usage from CC-Switch database...")
    print("  Close: click × on the overlay\n")

    overlay = TokenOverlay()
    overlay.run()


if __name__ == "__main__":
    main()
