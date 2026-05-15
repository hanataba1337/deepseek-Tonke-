"""Desktop overlay widget for real-time token usage display."""
import tkinter as tk

from tracker import get_tracker
from config import (
    OVERLAY_OPACITY, OVERLAY_WIDTH, OVERLAY_HEIGHT,
    OVERLAY_BG_COLOR, OVERLAY_FG_COLOR, OVERLAY_ACCENT_COLOR,
    OVERLAY_FONT, OVERLAY_TITLE_FONT,
)
from settings import get as get_setting, save as save_settings

LBL_TITLE = "  DeepSeek 用量监控"
LBL_STATUS = "读取 CC-Switch"
LBL_TODAY = "── 今日 ──"
LBL_MODELS = "── 模型 ──"
LBL_COST = "  费用:"
LBL_INPUT = "  输入:"
LBL_OUTPUT = "  输出:"
LBL_TOTAL = "  总计:"


class TokenOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DeepSeek Monitor")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", OVERLAY_OPACITY)
        self.root.geometry(f"{OVERLAY_WIDTH}x{OVERLAY_HEIGHT}+50+50")
        self.root.configure(bg=OVERLAY_BG_COLOR)

        self._drag_data = {"x": 0, "y": 0}
        self._build_ui()
        self._update()

    def _build_ui(self):
        main = tk.Frame(self.root, bg=OVERLAY_BG_COLOR,
                        highlightbackground=OVERLAY_ACCENT_COLOR, highlightthickness=1)
        main.pack(fill=tk.BOTH, expand=True)

        # ── title bar ──
        bar = tk.Frame(main, bg="#16213e", height=28)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)

        tk.Label(bar, text=LBL_TITLE, font=OVERLAY_TITLE_FONT,
                 bg="#16213e", fg=OVERLAY_ACCENT_COLOR).pack(side=tk.LEFT, fill=tk.Y)

        cb = tk.Label(bar, text=" × ", font=("Consolas", 14, "bold"),
                      bg="#16213e", fg="#ff6b6b", cursor="hand2")
        cb.pack(side=tk.RIGHT, padx=(0, 4))
        cb.bind("<Button-1>", self._close)

        bar.bind("<ButtonPress-1>", self._start_drag)
        bar.bind("<B1-Motion>", self._do_drag)

        # ── content ──
        c = tk.Frame(main, bg=OVERLAY_BG_COLOR, padx=12, pady=8)
        c.pack(fill=tk.BOTH, expand=True)

        # status
        sf = tk.Frame(c, bg=OVERLAY_BG_COLOR)
        sf.pack(fill=tk.X, pady=(0, 6))
        self.status_dot = tk.Canvas(sf, width=10, height=10,
                                     bg=OVERLAY_BG_COLOR, highlightthickness=0)
        self.status_dot.pack(side=tk.LEFT, padx=(0, 6))
        self._dot = self.status_dot.create_oval(1, 1, 9, 9, fill="#4caf50", outline="")
        tk.Label(sf, text=LBL_STATUS, font=("Consolas", 8),
                 bg=OVERLAY_BG_COLOR, fg="#4caf50").pack(side=tk.LEFT)

        self._sep(c)

        # ── today ──
        tk.Label(c, text=LBL_TODAY, font=OVERLAY_FONT,
                 bg=OVERLAY_BG_COLOR, fg=OVERLAY_ACCENT_COLOR).pack(anchor=tk.W, pady=(4, 2))

        self.today_labels = {}
        for key, text in [("prompt", LBL_INPUT), ("completion", LBL_OUTPUT), ("total", LBL_TOTAL)]:
            row = tk.Frame(c, bg=OVERLAY_BG_COLOR)
            row.pack(fill=tk.X)
            tk.Label(row, text=text, font=OVERLAY_FONT,
                     bg=OVERLAY_BG_COLOR, fg="#aaa").pack(side=tk.LEFT)
            lbl = tk.Label(row, text="0", font=OVERLAY_FONT,
                           bg=OVERLAY_BG_COLOR, fg=OVERLAY_FG_COLOR)
            lbl.pack(side=tk.RIGHT)
            self.today_labels[key] = lbl

        cost_row = tk.Frame(c, bg=OVERLAY_BG_COLOR)
        cost_row.pack(fill=tk.X, pady=(2, 0))
        tk.Label(cost_row, text=LBL_COST, font=OVERLAY_FONT,
                 bg=OVERLAY_BG_COLOR, fg="#aaa").pack(side=tk.LEFT)
        self.cost_label = tk.Label(cost_row, text="¥0.000000", font=OVERLAY_FONT,
                                    bg=OVERLAY_BG_COLOR, fg="#ffd54f")
        self.cost_label.pack(side=tk.RIGHT)

        # budget (editable)
        budget_row = tk.Frame(c, bg=OVERLAY_BG_COLOR)
        budget_row.pack(fill=tk.X)
        tk.Label(budget_row, text="  预算: ¥", font=OVERLAY_FONT,
                 bg=OVERLAY_BG_COLOR, fg="#aaa").pack(side=tk.LEFT)
        self.budget_var = tk.StringVar(value=str(get_setting("budget")))
        self.budget_entry = tk.Entry(budget_row, textvariable=self.budget_var,
                                      width=7, font=OVERLAY_FONT,
                                      bg="#16213e", fg=OVERLAY_ACCENT_COLOR,
                                      bd=0, highlightthickness=0,
                                      relief=tk.FLAT, insertbackground=OVERLAY_ACCENT_COLOR)
        self.budget_entry.pack(side=tk.LEFT, padx=(2, 0))
        self.budget_entry.bind("<Return>", self._save_budget)
        self.budget_entry.bind("<FocusOut>", self._save_budget)
        self.remain_label = tk.Label(budget_row, text="剩¥0.00", font=OVERLAY_FONT,
                                     bg=OVERLAY_BG_COLOR, fg="#4fc3f7")
        self.remain_label.pack(side=tk.RIGHT)

        self._sep(c)

        # ── models ──
        tk.Label(c, text=LBL_MODELS, font=OVERLAY_FONT,
                 bg=OVERLAY_BG_COLOR, fg=OVERLAY_ACCENT_COLOR).pack(anchor=tk.W, pady=(4, 2))
        self.model_frame = tk.Frame(c, bg=OVERLAY_BG_COLOR)
        self.model_frame.pack(fill=tk.X)

        self._sep(c)

        # debug
        self.debug_label = tk.Label(c, text="", font=("Consolas", 8),
                                     bg=OVERLAY_BG_COLOR, fg="#666")
        self.debug_label.pack(anchor=tk.W)

    def _sep(self, parent):
        tk.Frame(parent, height=1, bg="#2a2a4a").pack(fill=tk.X, pady=4)

    def _start_drag(self, event):
        self._drag_data["x"], self._drag_data["y"] = event.x, event.y

    def _do_drag(self, event):
        x = self.root.winfo_x() + event.x - self._drag_data["x"]
        y = self.root.winfo_y() + event.y - self._drag_data["y"]
        self.root.geometry(f"+{x}+{y}")

    def _close(self, event=None):
        self.root.quit()
        return "break"

    def _save_budget(self, event=None):
        try:
            v = float(self.budget_var.get())
            save_settings({"budget": v})
            self.budget_var.set(f"{v:.2f}")
            self.budget_entry.config(fg=OVERLAY_ACCENT_COLOR)
        except ValueError:
            self.budget_entry.config(fg="#f44336")

    def _update(self):
        try:
            t = get_tracker()
            today = t.get_today_usage()
            self.today_labels["prompt"].config(text=self._fmt(today["prompt"]))
            self.today_labels["completion"].config(text=self._fmt(today["completion"]))
            self.today_labels["total"].config(text=self._fmt(today["total"]))
            self.cost_label.config(text=f"¥{today['cost']:.4f}")

            used = t.get_monthly_cost()
            budget = float(self.budget_var.get() or get_setting("budget"))
            remain = budget - used
            color = "#f44336" if remain <= 0 else "#ffd54f" if remain < budget * 0.2 else "#4fc3f7"
            self.remain_label.config(text=f"剩¥{max(remain,0):.2f}", fg=color)

            self._update_model_rows(t.get_model_breakdown())

            self.debug_label.config(
                text=f"  请求: {t.get_request_count()}  状态: {t.get_last_status()}")
        except Exception as e:
            self.debug_label.config(text=f"  ⚠ {e}")
            self.status_dot.itemconfig(self._dot, fill="#f44336")

        self.root.after(2000, self._update)

    def _update_model_rows(self, models):
        for w in self.model_frame.winfo_children():
            w.destroy()
        placed = 0
        for m in models:
            if m["total"] == 0:
                continue
            row = tk.Frame(self.model_frame, bg=OVERLAY_BG_COLOR)
            row.pack(fill=tk.X)
            tk.Label(row, text=f"  {m['label']}", font=OVERLAY_FONT,
                     bg=OVERLAY_BG_COLOR,
                     fg="#ffd54f" if "pro" in (m["model"] or "") else OVERLAY_ACCENT_COLOR
                     ).pack(side=tk.LEFT)
            tk.Label(row, text=f"¥{m['cost']:.4f}", font=OVERLAY_FONT,
                     bg=OVERLAY_BG_COLOR, fg="#ffd54f").pack(side=tk.RIGHT)
            tk.Label(row, text=f"{self._fmt(m['total'])}", font=OVERLAY_FONT,
                     bg=OVERLAY_BG_COLOR, fg=OVERLAY_FG_COLOR
                     ).pack(side=tk.RIGHT, padx=(0, 6))
            placed += 1
        if placed == 0:
            tk.Label(self.model_frame, text="  暂无", font=OVERLAY_FONT,
                     bg=OVERLAY_BG_COLOR, fg="#666").pack(anchor=tk.W)

    @staticmethod
    def _fmt(n):
        if n >= 1_000_000:
            return f"{n/1_000_000:.2f}M"
        if n >= 1_000:
            return f"{n/1_000:.1f}K"
        return str(n)

    def run(self):
        self.root.mainloop()
