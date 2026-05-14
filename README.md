# DeepSeek Token Monitor 🖥️📊

> 💸 **你的每一分钱都花在哪了？让它在桌面上直接告诉你。**

实时监控 DeepSeek API Token 用量的桌面悬浮窗工具。  
透明代理 → 自动捕获 → 桌面实时显示。**改一行代码，打开即用。**

```bash
# 改之前
base_url="https://api.deepseek.com/v1"
# 改之后
base_url="http://127.0.0.1:8787/v1"
# 搞定，看桌面。
```

## 效果预览

```
┌─────────────────────────────────┐
│  DeepSeek Monitor          ×    │
│  ● Proxy Running               │
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

- **透明代理** — 本地启动代理服务器，透明转发 API 请求并自动捕获 token 用量
- **实时悬浮窗** — 桌面常驻半透明窗口，每 2 秒自动刷新
- **详细统计** — 输入/输出 Token 数、费用估算、今日累计、会话累计
- **持久化存储** — SQLite 存储历史用量，跨会话保留
- **零侵入** — 只需改一行 `base_url`，无需修改业务代码
- **流式支持** — 完整支持 streaming 和非 streaming 请求
- **可拖拽** — 鼠标拖拽标题栏任意摆放

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 设置 API Key

**方式一：环境变量（推荐）**
```bash
set DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**方式二：编辑 start.bat**
```batch
set DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> ⚠️ `start.bat` 已加入 `.gitignore`，不会误提交 API Key。
> 可参考 `start.bat.example` 创建自己的启动脚本。

### 3. 启动

```bash
python main.py
```

或者双击 `start.bat`。

启动后终端会显示：
```
DeepSeek Monitor is running!
Proxy:    http://127.0.0.1:8787
Overlay:  desktop widget active
```

桌面上会出现深色半透明悬浮窗。

### 4. 修改应用代码

将你的 DeepSeek API 地址指向本地代理：

```python
# 修改前
client = OpenAI(
    api_key="sk-xxx",
    base_url="https://api.deepseek.com/v1"
)

# 修改后
client = OpenAI(
    api_key="sk-xxx",           # 这里还是填真实的 API Key
    base_url="http://127.0.0.1:8787/v1"  # 代理地址
)
```

**通过环境变量配置（兼容 openai 库）：**
```bash
set OPENAI_BASE_URL=http://127.0.0.1:8787/v1
```

## 项目结构

```
deepseek-monitor/
├── main.py              # 主入口（启动代理 + 悬浮窗）
├── proxy.py             # 本地代理服务器（拦截 API 并统计用量）
├── tracker.py           # 用量追踪 + SQLite 持久化存储
├── overlay.py           # 桌面悬浮窗 UI（tkinter 透明窗口）
├── config.py            # 全局配置（API Key、价格、窗口样式等）
├── requirements.txt     # Python 依赖
├── start.bat            # Windows 一键启动脚本（已 gitignore）
├── start.bat.example    # 启动脚本模板（不含 Key）
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
| ● Proxy Running | 状态灯 | 绿色=运行中 |
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

## 数据存储

- **位置**: `~/.deepseek-monitor/usage.db`
- **内容**: 每次 API 调用的时间、模型、Token 数、费用
- **保留**: 自动持久化，不会丢失

## 常见问题

**Q: 需要改很多代码吗？**
A: 只需改一行 `base_url`，将 `https://api.deepseek.com/v1` 改为 `http://127.0.0.1:8787/v1`。

**Q: 会影响 API 响应速度吗？**
A: 代理只做转发和计数，几乎没有额外延迟（微秒级）。流式响应同样支持。

**Q: 只支持 DeepSeek 吗？**
A: 目前专为 DeepSeek API 设计，但代码结构通用，修改 `config.py` 中的 `DEEPSEEK_BASE_URL` 和 `PRICING` 即可适配其他 OpenAI 兼容 API。

**Q: tkinter 窗口看起来简陋？**
A: 是的，tkinter 就是原生风格。如果需要更现代的外观，可以改用 PyQt/PySide 重写 `overlay.py`。

## 许可证

MIT
