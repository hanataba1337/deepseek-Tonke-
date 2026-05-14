# DeepSeek Token Monitor 🖥️📊

> 💸 **你的每一分钱都花在哪了？让它在桌面上直接告诉你。**

实时监控 DeepSeek API Token 用量的桌面悬浮窗工具。  
**直接读取 CC-Switch 内部数据库**，零侵入，无需改任何配置。

```bash
pip install -r requirements.txt
python main.py
# 搞定，看桌面。
```

## 效果预览

```
┌─────────────────────────────────┐
│  DeepSeek Monitor          ×    │
│  ● Reading CC-Switch           │
│  ─────────────────────────     │
│  ── Today ──                   │
│    Input:     1,234            │
│    Output:      567            │
│    Total:     1,801            │
│    Cost:     $0.001234         │
│  ─────────────────────────     │
│  ── Session ──                 │
│    1,801 tot (in: 1,234  out: 567)
│    $0.001234                   │
│  ─────────────────────────     │
│  ── Last ──                    │
│    +200 in  +80 out  $0.000082 │
└─────────────────────────────────┘
```

## 功能特性

- **零侵入** — 直接从 CC-Switch 数据库读取数据，无需改任何代码或配置
- **实时悬浮窗** — 桌面常驻半透明窗口，每 2 秒自动刷新
- **详细统计** — 输入/输出 Token 数、费用估算、今日累计、会话累计
- **自动工作** — 只要你在用 CC-Switch 调 DeepSeek，打开就用
- **可拖拽** — 鼠标拖拽标题栏任意摆放

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动

```bash
python main.py
```

或者双击 `start.bat`。

> **前置条件**：需要已安装 [CC-Switch](https://cc-switch.com) 并配置了 DeepSeek 提供商。

## 工作原理

```
你发消息 → CC-Switch(15721端口) → DeepSeek 官方
                ↓
      CC-Switch 自动记录每次请求的 token 数到 SQLite 数据库
                ↓
      DeepSeek Monitor 读取该数据库并在悬浮窗显示
```

不需要代理，不需要修改任何配置，CC-Switch 本身就已经记录了所有用量数据。

## 项目结构

```
deepseek-monitor/
├── main.py              # 主入口
├── tracker.py           # 读取 CC-Switch 数据库获取用量
├── overlay.py           # 桌面悬浮窗 UI（tkinter 透明窗口）
├── config.py            # 配置（价格、窗口样式等）
├── requirements.txt     # Python 依赖
├── start.bat            # 一键启动脚本
└── .gitignore           # Git 忽略规则
```

## 悬浮窗交互

| 操作 | 说明 |
|------|------|
| **拖拽标题栏** | 移动悬浮窗到任意位置 |
| **点击 ×** | 关闭程序 |

### 显示内容说明

| 区域 | 数据 | 说明 |
|------|------|------|
| ● Reading CC-Switch | 状态灯 | 绿色=运行中 |
| ── Today ── | Input / Output / Total | 今日累计 Token 用量 |
| | Cost | 今日累计费用（USD） |
| ── Session ── | Token 明细 | 本次启动以来的用量 |
| | Cost | 本次会话费用 |
| ── Last ── | 最近一次请求 | 最后一次 API 调用的消耗 |

## 费用计算

默认价格（基于 DeepSeek 官方定价，USD/百万 Token）：

| 模型 | 输入 | 输出 |
|------|------|------|
| deepseek-chat / deepseek-v3 | $0.27 | $1.10 |
| deepseek-reasoner / deepseek-r1 | $0.55 | $2.19 |

可在 `config.py` 的 `PRICING` 字典中自定义。

## 数据来源

数据来自 **CC-Switch** 的 `proxy_request_logs` 表，位于：

```
%USERPROFILE%\.cc-switch\cc-switch.db
```

## 常见问题

**Q: 需要安装 CC-Switch 吗？**
A: 是的，本工具依赖 CC-Switch 记录的用量数据。如果你不用 CC-Switch，可以用 proxy 模式（旧版本）。

**Q: 会影响网络性能吗？**
A: 完全不会。本工具只读数据库，不代理任何网络请求。

**Q: 支持其他 API 提供商吗？**
A: 目前支持 DeepSeek（通过 CC-Switch），可以扩展 `tracker.py` 支持其他提供商。

**Q: tkinter 窗口看起来简陋？**
A: tkinter 就是原生风格，但轻量无依赖。可以用 PyQt 重写 `overlay.py` 获得更现代的外观。

## 许可证

MIT
