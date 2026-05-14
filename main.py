"""DeepSeek Token Monitor - Desktop overlay for real-time token usage.

直接从 CC-Switch 数据库读取用量数据，桌面悬浮窗实时显示。
无需代理、无需改配置。

Usage:
  pip install -r requirements.txt
  python main.py
"""
from overlay import TokenOverlay


def main():
    print("  DeepSeek 用量监控")
    print("  从 CC-Switch 读取用量数据...")
    print("  点击悬浮窗 × 退出\n")

    overlay = TokenOverlay()
    overlay.run()


if __name__ == "__main__":
    main()
