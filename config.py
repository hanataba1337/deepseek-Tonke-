"""Configuration for DeepSeek Token Monitor."""

# DeepSeek pricing per 1M tokens (USD)
# https://api-docs.deepseek.com/quick_start/pricing
PRICING = {
    "deepseek-chat": {"input": 0.27, "output": 1.10},
    "deepseek-reasoner": {"input": 0.55, "output": 2.19},
    "deepseek-v3": {"input": 0.27, "output": 1.10},
    "deepseek-r1": {"input": 0.55, "output": 2.19},
    "default": {"input": 0.27, "output": 1.10},
}

# Overlay window settings
OVERLAY_OPACITY = 0.85
OVERLAY_WIDTH = 280
OVERLAY_HEIGHT = 340
OVERLAY_BG_COLOR = "#1a1a2e"
OVERLAY_FG_COLOR = "#e0e0e0"
OVERLAY_ACCENT_COLOR = "#4fc3f7"
OVERLAY_FONT = ("Consolas", 10)
OVERLAY_TITLE_FONT = ("Consolas", 11, "bold")
