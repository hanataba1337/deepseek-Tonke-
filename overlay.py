"""Desktop overlay widget for real-time token usage display."""
import tkinter as tk

from tracker import get_tracker
from config import (
    OVERLAY_OPACITY, OVERLAY_WIDTH, OVERLAY_HEIGHT,
    OVERLAY_BG_COLOR, OVERLAY_FG_COLOR, OVERLAY_ACCENT_COLOR,
    OVERLAY_FONT, OVERLAY_TITLE_FONT,
)


class TokenOverlay:
    """Always-on-top, draggable, semi-transparent overlay widget."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DeepSeek Monitor")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", OVERLAY_OPACITY)
        self.root.geometry(f"{OVERLAY_WIDTH}x{OVERLAY_HEIGHT}+50+50")
        self.root.configure(bg=OVERLAY_BG_COLOR)

        # Drag state
        self._drag_data = {"x": 0, "y": 0}

        self._build_ui()
        self._update()

    def _build_ui(self):
        main = tk.Frame(self.root, bg=OVERLAY_BG_COLOR,
                        highlightbackground=OVERLAY_ACCENT_COLOR, highlightthickness=1)
        main.pack(fill=tk.BOTH, expand=True)

        # Title bar (draggable)
        title_bar = tk.Frame(main, bg="#16213e", height=28)
        title_bar.pack(fill=tk.X)
        title_bar.pack_propagate(False)

        tk.Label(title_bar, text="  DeepSeek Monitor", font=OVERLAY_TITLE_FONT,
                 bg="#16213e", fg=OVERLAY_ACCENT_COLOR).pack(side=tk.LEFT, fill=tk.Y)

        close_btn = tk.Label(title_bar, text=" × ", font=("Consolas", 14, "bold"),
                             bg="#16213e", fg="#ff6b6b", cursor="hand2")
        close_btn.pack(side=tk.RIGHT, padx=(0, 4))
        close_btn.bind("<Button-1>", lambda e: self.root.quit())

        # Bind drag to title bar (but not close button)
        title_bar.bind("<ButtonPress-1>", self._start_drag)
        title_bar.bind("<B1-Motion>", self._do_drag)
        # Re-bind close button to prevent drag
        close_btn.bind("<ButtonPress-1>", lambda e: None)

        # Content area
        content = tk.Frame(main, bg=OVERLAY_BG_COLOR, padx=12, pady=8)
        content.pack(fill=tk.BOTH, expand=True)

        # Status line
        status_frame = tk.Frame(content, bg=OVERLAY_BG_COLOR)
        status_frame.pack(fill=tk.X, pady=(0, 6))
        self.status_dot = tk.Canvas(status_frame, width=10, height=10,
                                    bg=OVERLAY_BG_COLOR, highlightthickness=0)
        self.status_dot.pack(side=tk.LEFT, padx=(0, 6))
        self._dot = self.status_dot.create_oval(1, 1, 9, 9, fill="#4caf50", outline="")
        tk.Label(status_frame, text="Proxy Running", font=("Consolas", 8),
                 bg=OVERLAY_BG_COLOR, fg="#4caf50").pack(side=tk.LEFT)

        self._add_separator(content)

        # ─── Today ───
        tk.Label(content, text="── Today ──", font=OVERLAY_FONT,
                 bg=OVERLAY_BG_COLOR, fg=OVERLAY_ACCENT_COLOR).pack(anchor=tk.W, pady=(4, 2))

        self.today_labels = {}
        for key, text in [("prompt", "Input"), ("completion", "Output"), ("total", "Total")]:
            row = tk.Frame(content, bg=OVERLAY_BG_COLOR)
            row.pack(fill=tk.X)
            tk.Label(row, text=f"  {text}:", font=OVERLAY_FONT,
                     bg=OVERLAY_BG_COLOR, fg="#aaa").pack(side=tk.LEFT)
            lbl = tk.Label(row, text="0", font=OVERLAY_FONT,
                           bg=OVERLAY_BG_COLOR, fg=OVERLAY_FG_COLOR)
            lbl.pack(side=tk.RIGHT)
            self.today_labels[key] = lbl

        # Cost row
        cost_row = tk.Frame(content, bg=OVERLAY_BG_COLOR)
        cost_row.pack(fill=tk.X, pady=(2, 0))
        tk.Label(cost_row, text="  Cost:", font=OVERLAY_FONT,
                 bg=OVERLAY_BG_COLOR, fg="#aaa").pack(side=tk.LEFT)
        self.cost_label = tk.Label(cost_row, text="$0.000000", font=OVERLAY_FONT,
                                   bg=OVERLAY_BG_COLOR, fg="#ffd54f")
        self.cost_label.pack(side=tk.RIGHT)

        self._add_separator(content)

        # ─── Session ───
        tk.Label(content, text="── Session ──", font=OVERLAY_FONT,
                 bg=OVERLAY_BG_COLOR, fg=OVERLAY_ACCENT_COLOR).pack(anchor=tk.W, pady=(4, 2))

        self.session_label = tk.Label(content, text="  0 tokens", font=OVERLAY_FONT,
                                      bg=OVERLAY_BG_COLOR, fg=OVERLAY_FG_COLOR)
        self.session_label.pack(anchor=tk.W)
        self.session_cost_label = tk.Label(content, text="  $0.000000", font=OVERLAY_FONT,
                                           bg=OVERLAY_BG_COLOR, fg="#ffd54f")
        self.session_cost_label.pack(anchor=tk.W)

        self._add_separator(content)

        # ─── Last Request ───
        tk.Label(content, text="── Last ──", font=OVERLAY_FONT,
                 bg=OVERLAY_BG_COLOR, fg=OVERLAY_ACCENT_COLOR).pack(anchor=tk.W, pady=(4, 2))
        self.last_label = tk.Label(content, text="  Waiting...", font=OVERLAY_FONT,
                                   bg=OVERLAY_BG_COLOR, fg="#888")
        self.last_label.pack(anchor=tk.W)

        # ─── Debug ───
        self._add_separator(content)
        self.debug_label = tk.Label(content, text="", font=("Consolas", 8),
                                     bg=OVERLAY_BG_COLOR, fg="#666")
        self.debug_label.pack(anchor=tk.W)

    def _add_separator(self, parent):
        sep = tk.Frame(parent, height=1, bg="#2a2a4a")
        sep.pack(fill=tk.X, pady=4)

    def _start_drag(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _do_drag(self, event):
        x = self.root.winfo_x() + event.x - self._drag_data["x"]
        y = self.root.winfo_y() + event.y - self._drag_data["y"]
        self.root.geometry(f"+{x}+{y}")

    def _update(self):
        try:
            tracker = get_tracker()
            today = tracker.get_today_usage()
            self.today_labels["prompt"].config(text=self._fmt(today["prompt"]))
            self.today_labels["completion"].config(text=self._fmt(today["completion"]))
            self.today_labels["total"].config(text=self._fmt(today["total"]))
            self.cost_label.config(text=f"${today['cost']:.6f}")

            session = tracker.get_session_usage()
            session_cost = tracker.get_session_cost()
            self.session_label.config(
                text=f"  {session['total']:,} tot  (in: {session['prompt']:,}  out: {session['completion']:,})")
            self.session_cost_label.config(text=f"  ${session_cost:.6f}")

            last = tracker.get_last_usage()
            if last:
                self.last_label.config(
                    text=f"  +{last['prompt']} in  +{last['completion']} out  ${last['cost']:.6f}")
                self.last_label.config(fg=OVERLAY_FG_COLOR)

            # Debug info
            req_count = tracker.get_request_count()
            last_status = tracker.get_last_status()
            self.debug_label.config(text=f"  reqs: {req_count}  status: {last_status}")
        except Exception:
            pass

        self.root.after(2000, self._update)

    @staticmethod
    def _fmt(n: int) -> str:
        if n >= 1_000_000:
            return f"{n/1_000_000:.2f}M"
        if n >= 1_000:
            return f"{n/1_000:.1f}K"
        return str(n)

    def run(self):
        self.root.mainloop()
