"""Configuration for DeepSeek Token Monitor."""
import os
from pathlib import Path

# DeepSeek API configuration
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

# Local proxy configuration
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 8787

# Pricing per 1M tokens (USD)
# https://api-docs.deepseek.com/quick_start/pricing
PRICING = {
    "deepseek-chat": {"input": 0.27, "output": 1.10},
    "deepseek-reasoner": {"input": 0.55, "output": 2.19},
    "deepseek-v3": {"input": 0.27, "output": 1.10},
    "deepseek-r1": {"input": 0.55, "output": 2.19},
    "default": {"input": 0.27, "output": 1.10},
}

# Data storage
DATA_DIR = Path.home() / ".deepseek-monitor"
DB_PATH = DATA_DIR / "usage.db"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Overlay window settings
OVERLAY_OPACITY = 0.85
OVERLAY_WIDTH = 280
OVERLAY_HEIGHT = 340
OVERLAY_BG_COLOR = "#1a1a2e"
OVERLAY_FG_COLOR = "#e0e0e0"
OVERLAY_ACCENT_COLOR = "#4fc3f7"
OVERLAY_FONT = ("Consolas", 10)
OVERLAY_TITLE_FONT = ("Consolas", 11, "bold")
