# DeepSeek Token Monitor 🖥️📊

> 💸 **See exactly where every cent of your API budget goes — right on your desktop.**

A real-time desktop overlay that monitors DeepSeek API token usage.  
**Reads directly from CC-Switch's internal database** — zero configuration, zero intrusion.

```bash
pip install -r requirements.txt
python main.py
# Done. Look at your desktop.
```

## Preview

```
┌─────────────────────────────────┐
│  DeepSeek Monitor          ×    │
│  ● Reading CC-Switch           │
│  ─────────────────────────     │
│  ── Today ──                   │
│    Input:     1,234            │
│    Output:      567            │
│    Total:     1,801            │
│    Cost:     ¥0.001234         │
│  ── Models ──                  │
│    V4-Flash    1,000  ¥0.0008  │
│    V4-Pro        801  ¥0.0004  │
│  ── Session ──                 │
│    1,801 tot(in:1,234 out:567) │
│    ¥0.001234                   │
│  ── Last ──                    │
│    V4-Flash +200in +80out ¥0.02│
└─────────────────────────────────┘
```

## Features

- **Zero intrusion** — Reads from CC-Switch's own database. No code changes, no config changes.
- **Real-time overlay** — Always-on-top, semi-transparent window, refreshes every 2 seconds.
- **Detailed stats** — Input/output tokens, cost estimates, today's totals, session totals.
- **Just works** — If you already use CC-Switch with DeepSeek, just run it.
- **Draggable** — Click and drag the title bar to reposition.

## Quick Start

### 1. Install

```bash
pip install -r requirements.txt
```

### 2. Run

```bash
python main.py
```

Or double-click `start.bat`.

> **Prerequisite**: [CC-Switch](https://cc-switch.com) must be installed and configured with a DeepSeek provider.

## How It Works

```
You send a message → CC-Switch (port 15721) → DeepSeek official API
                          ↓
            CC-Switch logs every request's token usage to SQLite
                          ↓
            DeepSeek Monitor reads the DB and displays on your desktop
```

No proxy needed. No configuration changes. CC-Switch already tracks all usage data.

## Project Structure

```
deepseek-monitor/
├── main.py              # Entry point
├── tracker.py           # Reads CC-Switch database for usage data
├── overlay.py           # Desktop overlay UI (tkinter)
├── config.py            # Configuration (pricing, window style)
├── requirements.txt     # Python dependencies
├── start.bat            # Windows launcher
└── .gitignore           # Git ignore rules
```

## Overlay Controls

| Action | Description |
|--------|-------------|
| **Drag title bar** | Move overlay anywhere |
| **Click ×** | Exit program |

### Display Fields

| Section | Data | Description |
|---------|------|-------------|
| ● Reading CC-Switch | Status dot | Green = active |
| ── Today ── | Input / Output / Total | Today's cumulative tokens |
| | Cost | Today's cumulative cost (USD) |
| ── Session ── | Token breakdown | Usage since this launch |
| | Cost | Session cost |
| ── Last ── | Most recent request | Last API call details |

## Pricing

Default pricing (DeepSeek official USD prices, converted to RMB at ~7.2, per million tokens):

| Model | Input | Output |
|-------|-------|--------|
| DeepSeek-V4-Flash | ¥1.00 | ¥2.00 |
| DeepSeek-V4-Pro | ¥3.10 | ¥6.30 |

Customize in `config.py` under the `PRICING` dictionary.

## Data Source

Data comes from **CC-Switch**'s `proxy_request_logs` table at:

```
%USERPROFILE%\.cc-switch\cc-switch.db
```

## FAQ

**Q: Do I need CC-Switch installed?**
A: Yes. This tool reads usage data from CC-Switch's database. If you don't use CC-Switch, check the git history for the proxy-based approach.

**Q: Does it affect network performance?**
A: No. It only reads a local database file — no network proxying involved.

**Q: Can I use it with other API providers?**
A: Currently supports DeepSeek via CC-Switch. Extend `tracker.py` to add more.

**Q: The tkinter window looks dated?**
A: It's native and dependency-free. Replace `overlay.py` with PyQt/PySide for a modern look.

## License

MIT
