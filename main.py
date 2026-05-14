"""DeepSeek Token Monitor - Desktop overlay for real-time token usage.

Usage:
  set DEEPSEEK_API_KEY=sk-xxxxxxxx  (or edit config.py)
  python main.py

Then in your app, use: base_url="http://127.0.0.1:8787/v1"
instead of:    base_url="https://api.deepseek.com/v1"

Or set environment variable:
  set OPENAI_BASE_URL=http://127.0.0.1:8787/v1
"""
import logging
import sys
import threading

from config import DEEPSEEK_API_KEY, PROXY_HOST, PROXY_PORT
from proxy import start_proxy
from overlay import TokenOverlay

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
log = logging.getLogger("main")


def main():
    if not DEEPSEEK_API_KEY:
        print("=" * 55)
        print("  DEEPSEEK_API_KEY not found!")
        print("  Set it as environment variable or in config.py")
        print()
        print("  Windows:  set DEEPSEEK_API_KEY=sk-xxxxxxxx")
        print("  Or edit  config.py  and set DEEPSEEK_API_KEY")
        print("=" * 55)
        sys.exit(1)

    # Start proxy in background thread
    proxy_thread = threading.Thread(target=start_proxy, daemon=True)
    proxy_thread.start()
    log.info("Proxy server started on %s:%s", PROXY_HOST, PROXY_PORT)

    print(f"\n  DeepSeek Monitor is running!")
    print(f"  Proxy:    http://{PROXY_HOST}:{PROXY_PORT}")
    print(f"  Overlay:  desktop widget active")
    print()
    print(f"  In your code, use:")
    print(f'    base_url="http://{PROXY_HOST}:{PROXY_PORT}/v1"')
    print(f"  Or set env: OPENAI_BASE_URL=http://{PROXY_HOST}:{PROXY_PORT}/v1")
    print(f"\n  Click × on the overlay to quit.\n")

    # Run overlay in main thread (required by tkinter on Windows)
    overlay = TokenOverlay()
    overlay.run()


if __name__ == "__main__":
    main()
