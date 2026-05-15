"""Persistent settings stored in settings.json."""
import json
import os
from pathlib import Path

_FILE = Path(__file__).parent / "settings.json"

DEFAULTS = {
    "budget": 50.0,
}


def load() -> dict:
    try:
        with open(_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return dict(DEFAULTS)


def save(data: dict):
    merged = dict(DEFAULTS)
    merged.update(data)
    with open(_FILE, "w") as f:
        json.dump(merged, f, indent=2)


def get(key: str):
    return load().get(key, DEFAULTS.get(key))
