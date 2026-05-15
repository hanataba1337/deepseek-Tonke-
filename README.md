# DeepSeek Token Monitor 🖥️📊

> 💸 **你的每一分钱都花在哪了？让它在桌面上直接告诉你。**

实时监控 DeepSeek API Token 用量的桌面悬浮窗工具。  
**双模式**：填入 API Key 走官方接口（费用精准），不填则读 CC-Switch 数据库（零配置）。

## 快速使用

**直接运行（无需安装 Python）：**

```
双击 DeepSeekMonitor.exe
```

**或者通过 Python 源码运行：**

```bash
pip install -r requirements.txt
python main.py
```

启动后在悬浮窗底部点 **`+ API`**，输入你的 DeepSeek API Key 按回车，费用数据即与官网一致。

> **没 Key 也能用** — 自动读取 CC-Switch 数据库中的用量数据。

## 效果预览

```
┌──────────────────────────────────┐
│  DeepSeek 用量监控           ×   │
│  ● DeepSeek API                  │  ← CC-Switch DB / API
│  ────────────────────────────    │
│  ── 今日 ──                     │
│    输入:                  1,234  │
│    输出:                    567  │
│    总计:                  1,801  │
│    费用:                ¥1.18    │  ← 官方接口精确费用
│    预算: ¥[50.00]     剩¥48.82   │
│  ── 模型 ──                     │
│    V4-Flash   1,000  ¥0.0008    │
│    V4-Pro       200  ¥0.0004    │
│  ────────────────────────────   │
│    请求: 108    状态: HTTP 200   │
│  + API                           │  ← 点开输入 Key
└──────────────────────────────────┘
```

## 功能特性

- **双模式** — 填入 API Key 走官方接口，不填自动读 CC-Switch 数据库
- **实时悬浮窗** — 桌面常驻半透明窗口，每 2 秒自动刷新，可拖拽
- **费用统计** — 今日输入/输出 Token 数及预估费用（API 模式精确到分）
- **月度预算** — 自行设定每月预算上限，实时显示已用/剩余，低于 20% 变色提醒
- **按模型拆分** — V4-Flash / V4-Pro 用量和费用分别显示
- **绿色免安装** — 提供单文件 exe，双击即用

## 悬浮窗交互

| 操作 | 说明 |
|------|------|
| **拖拽标题栏** | 移动悬浮窗到任意位置 |
| **点击 ×** | 关闭程序 |
| **编辑预算框** | 直接输入数字，回车保存 |
| **`+ API`** | 展开 API Key 输入框 |

### 显示内容

| 区域 | 说明 |
|------|------|
| ● 状态灯 + 数据源 | 绿色=运行中（显示当前使用 API 或 DB） |
| 今日 | Token 明细 + 官方精确费用（API 模式） |
| 预算 | 月度预算、已用金额、剩余金额 |
| 模型 | V4-Flash / V4-Pro 各自的用量及费用 |

## 工作原理

### 模式 A：填写 API Key（推荐）

```
DeepSeek Monitor
      ↓
  GET api.deepseek.com/v1/dashboard/billing/usage
      ↓
  官方费用数据，与官网完全一致
```

### 模式 B：CC-Switch 数据库（零配置）

```
你发消息 → CC-Switch(15721端口) → DeepSeek 官方
                ↓
      CC-Switch 自动记录每次请求到 SQLite 数据库
                ↓
      DeepSeek Monitor 读取数据库并显示
```

> 注意：CC-Switch 数据库可能只保留部分日志，费用为估算值。要获取精确费用请使用 API 模式。

## 项目结构

```
deepseek-monitor/
├── main.py              # 主入口
├── overlay.py           # 桌面悬浮窗 UI
├── tracker.py           # 用量数据获取（API + DB 双模式）
├── deepseek_api.py      # DeepSeek 官方 API 调用
├── settings.py          # 用户设置持久化
├── config.py            # 配置（价格、窗口样式等）
├── DeepSeekMonitor.exe  # 绿色免安装可执行文件
├── requirements.txt     # Python 依赖（源码运行需要）
├── start.bat            # 一键启动脚本
└── .gitignore           # Git 忽略规则
```

## 费用计算

API 模式：费用直接来自 DeepSeek 官方接口，与官网一致。

DB 模式（无 API Key）：基于 DeepSeek 官方定价，按 **95% 缓存命中率**计算有效输入价。

可在 `config.py` 中调整 `CACHE_HIT_RATE`（默认 0.95）和 `PRICING`。

## 常见问题

**Q: 一定要填 API Key 吗？**
A: 不用。不填 Key 自动走 CC-Switch 数据库，填了 Key 费用更精准。

**Q: 会影响网络性能吗？**
A: 不会。本工具只读数据库或查询用量接口，不代理任何请求。

**Q: 预算怎么改？**
A: 直接在悬浮窗的预算输入框里输入数字，按回车保存。

**Q: API Key 安全吗？**
A: 存在本地的 `settings.json` 文件中，仅用于查询用量，不会上传或泄露。

## 许可证

MIT
