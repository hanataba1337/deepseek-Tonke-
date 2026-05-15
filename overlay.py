"""Desktop overlay — balance tracking mode."""
import tkinter as tk

from tracker import get_tracker
from config import (
    OVERLAY_OPACITY, OVERLAY_WIDTH, OVERLAY_HEIGHT,
    OVERLAY_BG_COLOR, OVERLAY_FG_COLOR, OVERLAY_ACCENT_COLOR,
    OVERLAY_FONT, OVERLAY_TITLE_FONT,
)
from settings import get as get_setting, save as save_settings

LBL_TITLE = "  DeepSeek 用量监控"


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
        self.status_label = tk.Label(sf, text="等待 API Key...", font=("Consolas", 8),
                                      bg=OVERLAY_BG_COLOR, fg="#888")
        self.status_label.pack(side=tk.LEFT)

        self._sep(c)

        # ── today ──
        tk.Label(c, text="── 今日 ──", font=OVERLAY_FONT,
                 bg=OVERLAY_BG_COLOR, fg=OVERLAY_ACCENT_COLOR).pack(anchor=tk.W, pady=(4, 2))

        cost_row = tk.Frame(c, bg=OVERLAY_BG_COLOR)
        cost_row.pack(fill=tk.X)
        tk.Label(cost_row, text="  费用:", font=OVERLAY_FONT,
                 bg=OVERLAY_BG_COLOR, fg="#aaa").pack(side=tk.LEFT)
        self.cost_label = tk.Label(cost_row, text="¥0.0000", font=OVERLAY_FONT,
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

        # balance
        self.balance_label = tk.Label(c, text="", font=OVERLAY_FONT,
                                       bg=OVERLAY_BG_COLOR, fg="#4caf50")
        self.balance_label.pack(anchor=tk.W)

        self._sep(c)

        # ── debug / info ──
        self.debug_label = tk.Label(c, text="", font=("Consolas", 8),
                                     bg=OVERLAY_BG_COLOR, fg="#666")
        self.debug_label.pack(anchor=tk.W)

        # api key toggle
        self._api_visible = False
        self.api_toggle = tk.Label(c, text="  + API", font=("Consolas", 8),
                                    bg=OVERLAY_BG_COLOR, fg="#555", cursor="hand2")
        self.api_toggle.pack(anchor=tk.W)
        self.api_toggle.bind("<Button-1>", self._toggle_api)

        self.api_frame = tk.Frame(c, bg=OVERLAY_BG_COLOR)
        tk.Label(self.api_frame, text="  Key:", font=("Consolas", 8),
                 bg=OVERLAY_BG_COLOR, fg="#555").pack(side=tk.LEFT)
        self.api_key_var = tk.StringVar(value=get_setting("api_key") or "")
        self.api_key_entry = tk.Entry(self.api_frame, textvariable=self.api_key_var,
                                       font=("Consolas", 8), width=22,
                                       bg="#16213e", fg="#aaa",
                                       bd=0, highlightthickness=0,
                                       relief=tk.FLAT, show="*")
        self.api_key_entry.pack(side=tk.LEFT, padx=(2, 0))
        self.api_key_entry.bind("<Return>", self._save_api_key)
        self.api_key_entry.bind("<FocusOut>", self._save_api_key)

    def _toggle_api(self, event=None):
        self._api_visible = not self._api_visible
        if self._api_visible:
            self.api_frame.pack(fill=tk.X)
            self.api_toggle.config(text="  - API")
        else:
            self.api_frame.pack_forget()
            self.api_toggle.config(text="  + API")

    def _save_api_key(self, event=None):
        key = self.api_key_var.get().strip()
        if key:
            save_settings({"api_key": key})
            self.api_key_entry.config(fg="#4caf50")
        else:
            self.api_key_entry.config(fg="#888")

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
            t.update()

            if t.ok():
                bal = t.get_balance()
                today = t.get_today_usage()
                month = t.get_monthly_cost()

                self.status_label.config(text=f"余额 ¥{bal}", fg="#4caf50")
                self.status_dot.itemconfig(self._dot, fill="#4caf50")
                self.cost_label.config(text=f"¥{today['cost']:.4f}", fg="#ffd54f")

                budget = float(self.budget_var.get() or get_setting("budget"))
                remain = budget - month
                color = "#f44336" if remain <= 0 else "#ffd54f" if remain < budget * 0.2 else "#4fc3f7"
                self.remain_label.config(text=f"剩¥{max(remain,0):.2f}", fg=color)

                self.balance_label.config(text=f"  余额: ¥{bal}")
                self.debug_label.config(
                    text=f"  今日: ¥{today['cost']}  本月: ¥{month}  会话: ¥{t.get_session_spent()}")
            else:
                err = t.last_api_error()
                self.status_label.config(text="API Key 未设置" if not err else f"API 错误", fg="#ff6b6b")
                self.status_dot.itemconfig(self._dot, fill="#f44336")
                self.debug_label.config(text=f"  在底部 +API 输入 Key")
        except Exception as e:
            self.debug_label.config(text=f"  ⚠ {e}")
            self.status_dot.itemconfig(self._dot, fill="#f44336")

        self.root.after(2000, self._update)

    def run(self):
        self.root.mainloop()
