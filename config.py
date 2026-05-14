"""Configuration for DeepSeek Token Monitor."""

# DeepSeek pricing per 1M tokens (RMB ¥)
# Based on official pricing: https://api-docs.deepseek.com/quick_start/pricing
# USD → RMB exchange rate: ~7.2
PRICING = {
    "deepseek-v4-flash":   {"input": 1.0, "output": 2.0},
    "deepseek-v4-pro":     {"input": 3.1, "output": 6.3},
    "deepseek-chat":       {"input": 1.0, "output": 2.0},
    "deepseek-reasoner":   {"input": 3.1, "output": 6.3},
    "deepseek-v3":         {"input": 1.0, "output": 2.0},
    "deepseek-r1":         {"input": 3.1, "output": 6.3},
    "default":             {"input": 1.0, "output": 2.0},
}

# Model display names (friendly labels)
MODEL_LABELS = {
    "deepseek-v4-flash": "V4-Flash",
    "deepseek-v4-pro": "V4-Pro",
    "deepseek-chat": "Chat",
    "deepseek-reasoner": "Reasoner",
    "deepseek-v3": "V3",
    "deepseek-r1": "R1",
}

# Overlay window settings
OVERLAY_OPACITY = 0.85
OVERLAY_WIDTH = 400
OVERLAY_HEIGHT = 420
OVERLAY_BG_COLOR = "#1a1a2e"
OVERLAY_FG_COLOR = "#e0e0e0"
OVERLAY_ACCENT_COLOR = "#4fc3f7"
OVERLAY_FONT = ("Consolas", 10)
OVERLAY_TITLE_FONT = ("Consolas", 11, "bold")
