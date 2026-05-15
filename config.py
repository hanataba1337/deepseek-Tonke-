"""Configuration for DeepSeek Token Monitor."""

# Cache hit rate (95%–99.5% per DeepSeek official)
# Used to compute effective input price = cache_hit × hit_rate + cache_miss × (1 − hit_rate)
# Lower value = conservative (slightly higher estimated cost)
CACHE_HIT_RATE = 0.95

# DeepSeek pricing per 1M tokens (RMB ¥)
# Based on official pricing: https://api-docs.deepseek.com/quick_start/pricing
_PRICES = {
    "deepseek-v4-flash":   {"cache_input": 0.02, "input": 1.0, "output": 2.0},
    "deepseek-v4-pro":     {"cache_input": 0.025, "input": 3.0, "output": 6.0},
    "deepseek-chat":       {"cache_input": 0.02, "input": 1.0, "output": 2.0},
    "deepseek-reasoner":   {"cache_input": 0.025, "input": 3.1, "output": 6.3},
    "deepseek-v3":         {"cache_input": 0.02, "input": 1.0, "output": 2.0},
    "deepseek-r1":         {"cache_input": 0.025, "input": 3.1, "output": 6.3},
    "default":             {"cache_input": 0.02, "input": 1.0, "output": 2.0},
}

# Effective prices after applying cache hit rate
PRICING = {}
for _m, _p in _PRICES.items():
    eff_input = _p["cache_input"] * CACHE_HIT_RATE + _p["input"] * (1 - CACHE_HIT_RATE)
    PRICING[_m] = {"input": round(eff_input, 4), "output": _p["output"]}

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
OVERLAY_WIDTH = 260
OVERLAY_HEIGHT = 350
OVERLAY_BG_COLOR = "#1a1a2e"
OVERLAY_FG_COLOR = "#e0e0e0"
OVERLAY_ACCENT_COLOR = "#4fc3f7"
OVERLAY_FONT = ("Consolas", 10)
OVERLAY_TITLE_FONT = ("Consolas", 11, "bold")
