# Action Recorder 设计文档

## 概述

在cli-anything-web-plugin中添加行为录制功能，录制用户的UI交互和HTTP流量，生成可重放的CLI工具并封装为skill。

## 目标

- 录制用户在网页上的操作行为（click, fill, submit等）
- 同时捕获触发的HTTP请求/响应
- 让用户选择动态字段参数化
- 生成可重放的CLI命令
- 封装为skill供后续调用

## 功能范围（第一阶段）

本阶段实现：
1. **录制功能** — 捕获UI事件 + HTTP流量
2. **接口重放CLI** — 将录制转换为API调用

第二阶段实现：
- Playwright脚本重放
- skill封装

## 架构设计

### 核心组件

```
cli-anything-web-plugin/
├── commands/
│   └── action-record.md      # 录制命令入口
├── skills/
│   ├── action-record/        # 录制skill
│   │   └── SKILL.md
│   └── action-replay/        # 重放skill
│       └── SKILL.md
└── scripts/
    ├── action-recorder/
    │   ├── __init__.py
    │   ├── recorder.py        # 录制核心逻辑
    │   ├── parser.py          # 解析录制数据
    │   ├── analyzer.py        # 智能识别动态字段
    │   └── generator.py       # 生成重放代码
    └── action-replay.py      # CLI入口
```

### 数据格式

```json
{
  "version": "1.0",
  "url": "https://example.com/form",
  "timestamp": "2026-04-02T10:00:00Z",
  "actions": [
    {
      "type": "click",
      "selector": "#submit-btn",
      "xpath": "//button[@id='submit-btn']",
      "timestamp": "2026-04-02T10:00:05.123Z"
    },
    {
      "type": "fill",
      "selector": "#username",
      "value": "testuser",
      "timestamp": "2026-04-02T10:00:03.456Z"
    }
  ],
  "http_requests": [
    {
      "id": "req-1",
      "action_ref": "click-submit-btn",
      "method": "POST",
      "url": "https://example.com/api/submit",
      "headers": {...},
      "body": {...},
      "response": {...},
      "timestamp": "2026-04-02T10:00:05.200Z"
    }
  ],
  "metadata": {
    "page_title": "Form Page",
    "user_agent": "...",
    "viewport": {"width": 1920, "height": 1080}
  }
}
```

### 关键设计决策

1. **录制方式**：基于playwright-cli扩展
   - 用`page.evaluate()`注入JS监听DOM事件（click, input, change, submit）
   - 用playwright的`page.on('request/response')`捕获HTTP
   - 时间戳对齐UI事件和HTTP请求

2. **动态字段识别**
   - 自动识别：token, timestamp, nonce, uuid, session等常见模式
   - 用户通过交互式提示选择额外字段参数化
   - 用`{{variable_name}}`占位符替换

3. **重放CLI**
   - 命令：`cli-web-action-replay <recording.json>`
   - 参数：动态字段通过CLI参数传入
   - 输出：JSON格式，包含执行结果

## 实现步骤

### 阶段1：录制功能

1. 创建 `scripts/action-recorder/` 目录
2. 实现 `recorder.py` — playwright事件监听 + HTTP捕获
3. 创建 `commands/action-record.md` 命令
4. 创建 `skills/action-record/SKILL.md`

### 阶段2：解析与参数化

1. 实现 `analyzer.py` — 智能识别动态字段
2. 实现 `parser.py` — 解析录制数据，关联UI事件和HTTP请求
3. 添加交互式参数选择UI

### 阶段3：接口重放

1. 实现 `generator.py` — 生成httpx调用代码
2. 创建 `action-replay.py` — CLI入口
3. 创建 `skills/action-replay/SKILL.md`

## 依赖

- playwright
- click
- httpx
- rich

## 验收标准

- [ ] 录制生成的JSON包含UI事件和HTTP请求
- [ ] UI事件和HTTP请求通过时间戳关联
- [ ] 智能识别常见动态字段（token, timestamp等）
- [ ] 用户可选择额外参数化字段
- [ ] 生成的CLI可独立重放录制的操作
- [ ] 重放CLI支持参数传入动态值

## 待讨论

- skill命名规范
- 与现有capture流程的集成点