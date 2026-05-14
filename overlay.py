"""Desktop overlay widget for real-time token usage display."""
import tkinter as tk

from tracker import get_tracker
from config import (
    OVERLAY_OPACITY, OVERLAY_WIDTH, OVERLAY_HEIGHT,
    OVERLAY_BG_COLOR, OVERLAY_FG_COLOR, OVERLAY_ACCENT_COLOR,
    OVERLAY_FONT, OVERLAY_TITLE_FONT,
)

# ── 界面文字 ──
LBL_TITLE = "  DeepSeek 用量监控"
LBL_STATUS = "读取 CC-Switch"
LBL_TODAY = "── 今日 ──"
LBL_MODELS = "── 模型 ──"
LBL_SESSION = "── 会话 ──"
LBL_LAST = "── 最近 ──"
LBL_COST = "  费用:"
LBL_WAITING = "  等待中..."
LBL_INPUT = "  输入:"
LBL_OUTPUT = "  输出:"
LBL_TOTAL = "  总计:"


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

        self._drag_data = {"x": 0, "y": 0}
        self._model_rows = []  # per-model display rows

        self._build_ui()
        self._update()

    def _build_ui(self):
        main = tk.Frame(self.root, bg=OVERLAY_BG_COLOR,
                        highlightbackground=OVERLAY_ACCENT_COLOR, highlightthickness=1)
        main.pack(fill=tk.BOTH, expand=True)

        # ── 标题栏（可拖拽） ──
        title_bar = tk.Frame(main, bg="#16213e", height=28)
        title_bar.pack(fill=tk.X)
        title_bar.pack_propagate(False)

        tk.Label(title_bar, text=LBL_TITLE, font=OVERLAY_TITLE_FONT,
                 bg="#16213e", fg=OVERLAY_ACCENT_COLOR).pack(side=tk.LEFT, fill=tk.Y)

        close_btn = tk.Label(title_bar, text=" × ", font=("Consolas", 14, "bold"),
                             bg="#16213e", fg="#ff6b6b", cursor="hand2")
        close_btn.pack(side=tk.RIGHT, padx=(0, 4))
        close_btn.bind("<Button-1>", lambda e: self.root.quit())

        title_bar.bind("<ButtonPress-1>", self._start_drag)
        title_bar.bind("<B1-Motion>", self._do_drag)
        close_btn.bind("<ButtonPress-1>", lambda e: None)

        # ── 内容区域 ──
        content = tk.Frame(main, bg=OVERLAY_BG_COLOR, padx=12, pady=8)
        content.pack(fill=tk.BOTH, expand=True)

        # 状态行
        status_frame = tk.Frame(content, bg=OVERLAY_BG_COLOR)
        status_frame.pack(fill=tk.X, pady=(0, 6))
        self.status_dot = tk.Canvas(status_frame, width=10, height=10,
                                    bg=OVERLAY_BG_COLOR, highlightthickness=0)
        self.status_dot.pack(side=tk.LEFT, padx=(0, 6))
        self._dot = self.status_dot.create_oval(1, 1, 9, 9, fill="#4caf50", outline="")
        tk.Label(status_frame, text=LBL_STATUS, font=("Consolas", 8),
                 bg=OVERLAY_BG_COLOR, fg="#4caf50").pack(side=tk.LEFT)

        self._add_sep(content)

        # ── 今日 ──
        tk.Label(content, text=LBL_TODAY, font=OVERLAY_FONT,
                 bg=OVERLAY_BG_COLOR, fg=OVERLAY_ACCENT_COLOR).pack(anchor=tk.W, pady=(4, 2))

        self.today_labels = {}
        for key, text in [("prompt", LBL_INPUT), ("completion", LBL_OUTPUT), ("total", LBL_TOTAL)]:
            row = tk.Frame(content, bg=OVERLAY_BG_COLOR)
            row.pack(fill=tk.X)
            tk.Label(row, text=text, font=OVERLAY_FONT,
                     bg=OVERLAY_BG_COLOR, fg="#aaa").pack(side=tk.LEFT)
            lbl = tk.Label(row, text="0", font=OVERLAY_FONT,
                           bg=OVERLAY_BG_COLOR, fg=OVERLAY_FG_COLOR)
            lbl.pack(side=tk.RIGHT)
            self.today_labels[key] = lbl

        cost_row = tk.Frame(content, bg=OVERLAY_BG_COLOR)
        cost_row.pack(fill=tk.X, pady=(2, 0))
        tk.Label(cost_row, text=LBL_COST, font=OVERLAY_FONT,
                 bg=OVERLAY_BG_COLOR, fg="#aaa").pack(side=tk.LEFT)
        self.cost_label = tk.Label(cost_row, text="¥0.000000", font=OVERLAY_FONT,
                                   bg=OVERLAY_BG_COLOR, fg="#ffd54f")
        self.cost_label.pack(side=tk.RIGHT)

        self._add_sep(content)

        # ── 模型用量 ──
        tk.Label(content, text=LBL_MODELS, font=OVERLAY_FONT,
                 bg=OVERLAY_BG_COLOR, fg=OVERLAY_ACCENT_COLOR).pack(anchor=tk.W, pady=(4, 2))
        self.model_frame = tk.Frame(content, bg=OVERLAY_BG_COLOR)
        self.model_frame.pack(fill=tk.X)

        self._add_sep(content)

        # ── 会话 ──
        tk.Label(content, text=LBL_SESSION, font=OVERLAY_FONT,
                 bg=OVERLAY_BG_COLOR, fg=OVERLAY_ACCENT_COLOR).pack(anchor=tk.W, pady=(4, 2))
        self.session_label = tk.Label(content, text="  0 tokens", font=OVERLAY_FONT,
                                      bg=OVERLAY_BG_COLOR, fg=OVERLAY_FG_COLOR)
        self.session_label.pack(anchor=tk.W)
        self.session_cost_label = tk.Label(content, text="  ¥0.000000", font=OVERLAY_FONT,
                                           bg=OVERLAY_BG_COLOR, fg="#ffd54f")
        self.session_cost_label.pack(anchor=tk.W)

        self._add_sep(content)

        # ── 最近 ──
        tk.Label(content, text=LBL_LAST, font=OVERLAY_FONT,
                 bg=OVERLAY_BG_COLOR, fg=OVERLAY_ACCENT_COLOR).pack(anchor=tk.W, pady=(4, 2))
        self.last_label = tk.Label(content, text=LBL_WAITING, font=OVERLAY_FONT,
                                   bg=OVERLAY_BG_COLOR, fg="#888")
        self.last_label.pack(anchor=tk.W)

        self._add_sep(content)

        # 调试
        self.debug_label = tk.Label(content, text="", font=("Consolas", 8),
                                     bg=OVERLAY_BG_COLOR, fg="#666")
        self.debug_label.pack(anchor=tk.W)

    def _add_sep(self, parent):
        tk.Frame(parent, height=1, bg="#2a2a4a").pack(fill=tk.X, pady=4)

    def _start_drag(self, event):
        self._drag_data["x"], self._drag_data["y"] = event.x, event.y

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
            self.cost_label.config(text=f"¥{today['cost']:.4f}")

            # Model breakdown
            models = tracker.get_model_breakdown()
            self._update_model_rows(models)

            # Session
            session = tracker.get_session_usage()
            sc = tracker.get_session_cost()
            self.session_label.config(
                text=f"  {session['total']:,} 总  (入:{session['prompt']:,}  出:{session['completion']:,})")
            self.session_cost_label.config(text=f"  ¥{sc:.6f}")

            # Last
            last = tracker.get_last_usage()
            if last:
                self.last_label.config(
                    text=f"  {last['label']}  +{self._fmt(last['prompt'])}入  +{self._fmt(last['completion'])}出  ¥{last['cost']:.4f}")
                self.last_label.config(fg=OVERLAY_FG_COLOR)

            self.debug_label.config(
                text=f"  请求: {tracker.get_request_count()}  状态: {tracker.get_last_status()}")
        except Exception:
            pass

        self.root.after(2000, self._update)

    def _update_model_rows(self, models: list):
        # Destroy old rows
        for widget in self.model_frame.winfo_children():
            widget.destroy()

        placed = 0
        for m in models:
            if m["total"] == 0:
                continue
            row = tk.Frame(self.model_frame, bg=OVERLAY_BG_COLOR)
            row.pack(fill=tk.X)
            # label + token count on left, cost on right
            tk.Label(row, text=f"  {m['label']}", font=OVERLAY_FONT,
                     bg=OVERLAY_BG_COLOR, fg=self._model_color(m["model"])).pack(side=tk.LEFT)
            tk.Label(row, text=f"¥{m['cost']:.4f}", font=OVERLAY_FONT,
                     bg=OVERLAY_BG_COLOR, fg="#ffd54f").pack(side=tk.RIGHT)
            tk.Label(row, text=f"{self._fmt(m['total'])}", font=OVERLAY_FONT,
                     bg=OVERLAY_BG_COLOR, fg=OVERLAY_FG_COLOR).pack(side=tk.RIGHT, padx=(0, 6))
            placed += 1

        if placed == 0:
            tk.Label(self.model_frame, text="  暂无", font=OVERLAY_FONT,
                     bg=OVERLAY_BG_COLOR, fg="#666").pack(anchor=tk.W)

    @staticmethod
    def _model_color(model: str) -> str:
        if "pro" in (model or ""):
            return "#ffd54f"
        return "#4fc3f7"

    @staticmethod
    def _fmt(n: int) -> str:
        if n >= 1_000_000:
            return f"{n/1_000_000:.2f}M"
        if n >= 1_000:
            return f"{n/1_000:.1f}K"
        return str(n)

    def run(self):
        self.root.mainloop()
