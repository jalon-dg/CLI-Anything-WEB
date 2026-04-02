# Action Recorder 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现行为录制功能，捕获UI事件+HTTP流量，生成可重放的CLI工具

**Architecture:** 基于playwright-cli扩展，用page.evaluate()注入JS监听DOM事件，用page.on()捕获HTTP请求，时间戳对齐UI事件和HTTP请求

**Tech Stack:** Python, playwright, click, httpx, rich

---

## 文件结构

```
cli-anything-web-plugin/
├── commands/
│   └── action-record.md          # 录制命令入口
├── skills/
│   ├── action-record/
│   │   └── SKILL.md               # 录制skill
│   └── action-replay/
│       └── SKILL.md               # 重放skill
├── scripts/
│   └── action-recorder/
│       ├── __init__.py
│       ├── recorder.py            # 录制核心逻辑
│       ├── parser.py              # 解析录制数据
│       ├── analyzer.py            # 智能识别动态字段
│       └── generator.py           # 生成重放代码
└── action-replay.py               # CLI入口
```

---

## Task 1: 创建项目结构和基础模块

**Files:**
- Create: `cli-anything-web-plugin/scripts/action-recorder/__init__.py`
- Create: `cli-anything-web-plugin/scripts/action-recorder/recorder.py`

- [ ] **Step 1: 创建__init__.py**

```python
"""Action Recorder - 录制UI交互和HTTP流量"""

__version__ = "1.0.0"
```

- [ ] **Step 2: 创建recorder.py基础结构**

```python
"""录制核心逻辑 - 使用playwright捕获UI事件和HTTP流量"""

from playwright.sync_api import sync_playwright, Page, Browser
from typing import Dict, List, Any, Callable
import json
from datetime import datetime


class ActionRecorder:
    """录制用户在网页上的操作行为和HTTP流量"""
    
    def __init__(self, output_path: str):
        self.output_path = output_path
        self.actions: List[Dict] = []
        self.http_requests: List[Dict] = []
        self.browser: Browser = None
        self.page: Page = None
    
    def start(self, url: str):
        """启动录制"""
        with sync_playwright() as p:
            self.browser = p.chromium.launch(headless=False)
            self.page = self.browser.new_page()
            
            # 注入JS监听DOM事件
            self._inject_event_listeners()
            
            # 监听HTTP请求
            self.page.on("request", self._on_request)
            self.page.on("response", self._on_response)
            
            # 导航到目标URL
            self.page.goto(url)
            
            print("录制已开始，请在浏览器中进行操作...")
            print("完成后关闭浏览器窗口结束录制")
            
            # 等待用户关闭浏览器
            self.page.context.wait_for_event("close")
            self._save()
    
    def _inject_event_listeners(self):
        """注入JS监听DOM事件"""
        js_code = """
        window.__actionRecorderEvents = [];
        ['click', 'input', 'change', 'submit'].forEach(eventType => {
            document.addEventListener(eventType, function(e) {
                const target = e.target;
                const event = {
                    type: eventType,
                    selector: target.id ? '#' + target.id : 
                              target.className ? '.' + target.className.split(' ').join('.') : 
                              target.tagName.toLowerCase(),
                    tagName: target.tagName,
                    id: target.id,
                    className: target.className,
                    value: target.value || null,
                    timestamp: new Date().toISOString()
                };
                window.__actionRecorderEvents.push(event);
                console.log('[ACTION_RECORDER]', JSON.stringify(event));
            }, true);
        });
        """
        self.page.evaluate(js_code)
    
    def _on_request(self, request):
        """捕获HTTP请求"""
        # 记录请求
        pass
    
    def _on_response(self, response):
        """捕获HTTP响应"""
        pass
    
    def _save(self):
        """保存录制结果"""
        data = {
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "actions": self.actions,
            "http_requests": self.http_requests
        }
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"录制已保存到: {self.output_path}")


if __name__ == "__main__":
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    output = sys.argv[2] if len(sys.argv) > 2 else "recording.json"
    recorder = ActionRecorder(output)
    recorder.start(url)
```

- [ ] **Step 3: 运行测试验证**

Run: `cd cli-anything-web-plugin && python -c "from scripts.action_recorder import ActionRecorder; print('OK')"`
Expected: OK

- [ ] **Step 4: Commit**

```bash
git add cli-anything-web-plugin/scripts/action-recorder/
git commit -m "feat(action-recorder): add recorder module structure

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 2: 完善HTTP请求捕获

**Files:**
- Modify: `cli-anything-web-plugin/scripts/action-recorder/recorder.py`

- [ ] **Step 1: 添加HTTP请求捕获逻辑**

在recorder.py中补充_on_request和_on_response方法：

```python
def __init__(self, output_path: str):
    self.output_path = output_path
    self.actions: List[Dict] = []
    self.http_requests: List[Dict] = []
    self._pending_requests: Dict[str, Dict] = {}
    self.browser: Browser = None
    self.page: Page = None

def _on_request(self, request):
    """捕获HTTP请求"""
    self._pending_requests[request.url] = {
        "method": request.method,
        "url": request.url,
        "headers": dict(request.headers),
        "post_data": request.post_data,
        "timestamp": datetime.now().isoformat()
    }

def _on_response(self, response):
    """捕获HTTP响应"""
    url = response.url
    if url in self._pending_requests:
        req_data = self._pending_requests.pop(url)
        try:
            body = response.text() if response.status < 500 else None
        except:
            body = None
        
        self.http_requests.append({
            "id": f"req-{len(self.http_requests) + 1}",
            "method": req_data["method"],
            "url": req_data["url"],
            "headers": req_data["headers"],
            "body": req_data.get("post_data"),
            "response": {
                "status": response.status,
                "headers": dict(response.headers),
                "body": body
            },
            "timestamp": req_data["timestamp"]
        })
```

- [ ] **Step 2: 添加UI事件提取逻辑**

在recorder.py中补充从page提取UI事件的方法：

```python
def _extract_ui_events(self):
    """从页面提取UI事件"""
    events = self.page.evaluate("""() => {
        const events = window.__actionRecorderEvents || [];
        window.__actionRecorderEvents = [];  # 清空
        return events;
    }""")
    for event in events:
        self.actions.append({
            "type": event["type"],
            "selector": event.get("selector"),
            "tag_name": event.get("tagName"),
            "id": event.get("id"),
            "value": event.get("value"),
            "timestamp": event.get("timestamp")
        })
```

- [ ] **Step 3: 修改_save方法提取UI事件**

```python
def _save(self):
    # 先提取UI事件
    self._extract_ui_events()
    
    # 计算action_ref，关联HTTP请求和UI事件
    self._link_actions_to_requests()
    
    data = {
        "version": "1.0",
        "timestamp": datetime.now().isoformat(),
        "actions": self.actions,
        "http_requests": self.http_requests,
        "metadata": {
            "page_title": self.page.title() if self.page else "",
            "url": self.page.url if self.page else ""
        }
    }
    with open(self.output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"录制已保存到: {self.output_path}")

def _link_actions_to_requests(self):
    """通过时间戳关联UI事件和HTTP请求"""
    if not self.actions or not self.http_requests:
        return
    
    # 按时间戳排序
    self.actions.sort(key=lambda x: x.get("timestamp", ""))
    self.http_requests.sort(key=lambda x: x.get("timestamp", ""))
    
    # 为每个HTTP请求关联最近的UI事件
    for req in self.http_requests:
        req_time = req.get("timestamp", "")
        for action in reversed(self.actions):
            action_time = action.get("timestamp", "")
            if action_time <= req_time:
                req["action_ref"] = action.get("selector", "unknown")
                break
```

- [ ] **Step 4: Commit**

```bash
git add cli-anything-web-plugin/scripts/action-recorder/recorder.py
git commit -m "feat(action-recorder): add HTTP request capturing

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 3: 创建录制命令和Skill

**Files:**
- Create: `cli-anything-web-plugin/commands/action-record.md`
- Create: `cli-anything-web-plugin/skills/action-record/SKILL.md`

- [ ] **Step 1: 创建commands/action-record.md**

```markdown
---
name: action-record
description: 录制用户在网页上的UI交互和HTTP流量，生成可重放的录制文件
argument-hint: <url> [--output <file>] [--duration <seconds>]
allowed-tools: Bash(*), Read, Write
---

# Action Record - 行为录制

录制用户在网页上的操作行为和触发的HTTP请求，用于生成可重放的CLI。

## 使用方法

```bash
# 基本用法
python cli-anything-web-plugin/scripts/action-recorder/recorder.py <url>

# 指定输出文件
python cli-anything-web-plugin/scripts/action-recorder/recorder.py <url> --output recording.json
```

## 录制内容

- UI事件：click, input, change, submit
- HTTP请求：method, url, headers, body
- HTTP响应：status, headers, body
- 关联：UI事件和HTTP请求通过时间戳自动关联

## 输出

生成JSON文件，包含actions和http_requests数组，可用于后续重放。
```

- [ ] **Step 2: 创建skills/action-record/SKILL.md**

```markdown
---
name: cli-anything-web:action-record
description: 录制用户在网页上的UI交互和HTTP流量
argument-hint: <url> [--output <file>]
trigger: "录制操作", "record actions", "录制表单", "capture UI"
version: 1.0.0
---

# Action Record - 行为录制

## 目标

录制用户在网页上的操作行为和触发的HTTP请求，生成可重放的JSON文件。

## 前置条件

- [ ] 安装playwright: `pip install playwright && playwright install chromium`
- [ ] 目标URL

## 步骤

### Step 1: 启动录制

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/action-recorder/recorder.py <url> [--output <file>]
```

### Step 2: 执行操作

在打开的浏览器窗口中执行你想要录制的操作：
- 填写表单字段
- 点击按钮
- 提交表单
- 导航到其他页面

### Step 3: 结束录制

关闭浏览器窗口，录制自动保存到JSON文件。

### Step 4: 分析录制结果

运行 analyzer 分析动态字段：
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/action-recorder/analyzer.py <recording.json>
```

## 输出

生成JSON文件，包含：
- `actions`: UI事件列表
- `http_requests`: HTTP请求/响应列表
- `metadata`: 页面元信息
```

- [ ] **Step 3: Commit**

```bash
git add cli-anything-web-plugin/commands/action-record.md cli-anything-web-plugin/skills/action-record/
git commit -m "feat(action-recorder): add action-record command and skill

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 4: 实现动态字段分析器

**Files:**
- Create: `cli-anything-web-plugin/scripts/action-recorder/analyzer.py`

- [ ] **Step 1: 创建analyzer.py**

```python
"""智能识别动态字段 - 分析录制数据，识别需要参数化的字段"""

import json
import re
from typing import Dict, List, Set, Tuple
from pathlib import Path


# 常见的动态字段模式
DYNAMIC_PATTERNS = {
    "token": r"(?i)(token|access_token|auth_token|jwt)",
    "timestamp": r"(?i)(timestamp|time|ts|date|created_at|updated_at)",
    "nonce": r"(?i)(nonce|csrf|csrf_token|xsrf)",
    "session": r"(?i)(session|session_id|sid)",
    "uuid": r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    "id": r"(?i)(_id|user_id|item_id|object_id)",
}


class DynamicFieldAnalyzer:
    """分析录制数据，识别动态字段"""
    
    def __init__(self, recording_path: str):
        self.recording_path = Path(recording_path)
        with open(recording_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.dynamic_fields: Set[str] = set()
    
    def analyze(self) -> Dict:
        """分析并识别动态字段"""
        self._analyze_http_requests()
        return self.get_report()
    
    def _analyze_http_requests(self):
        """分析HTTP请求中的动态字段"""
        for req in self.data.get("http_requests", []):
            # 分析URL中的动态参数
            self._analyze_url(req.get("url", ""))
            
            # 分析请求体
            body = req.get("body")
            if body:
                self._analyze_json(body)
            
            # 分析响应体
            response = req.get("response", {})
            resp_body = response.get("body")
            if resp_body:
                self._analyze_json(resp_body)
    
    def _analyze_url(self, url: str):
        """分析URL中的动态参数"""
        # 提取查询参数
        if "?" in url:
            query = url.split("?")[1]
            params = query.split("&")
            for param in params:
                if "=" in param:
                    key = param.split("=")[0]
                    if self._is_dynamic_key(key):
                        self.dynamic_fields.add(key)
    
    def _analyze_json(self, data):
        """分析JSON数据中的动态字段"""
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except:
                return
        
        if isinstance(data, dict):
            for key, value in data.items():
                if self._is_dynamic_key(key):
                    self.dynamic_fields.add(key)
                elif isinstance(value, str) and self._is_dynamic_value(value):
                    self.dynamic_fields.add(key)
                elif isinstance(value, dict):
                    self._analyze_json(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            self._analyze_json(item)
    
    def _is_dynamic_key(self, key: str) -> bool:
        """判断键名是否为动态字段"""
        key_lower = key.lower()
        for pattern_name, pattern in DYNAMIC_PATTERNS.items():
            if re.search(pattern, key_lower):
                return True
        return False
    
    def _is_dynamic_value(self, value: str) -> bool:
        """判断值是否为动态值"""
        # UUID
        if re.match(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", value):
            return True
        # 长时间戳
        if re.match(r"^\d{10,13}$", value):
            return True
        # Base64 token (长字符串)
        if len(value) > 50 and re.match(r"^[A-Za-z0-9_-]+$", value):
            return True
        return False
    
    def get_report(self) -> Dict:
        """获取分析报告"""
        return {
            "total_requests": len(self.data.get("http_requests", [])),
            "total_actions": len(self.data.get("actions", [])),
            "dynamic_fields": sorted(list(self.dynamic_fields)),
            "recommendations": self._get_recommendations()
        }
    
    def _get_recommendations(self) -> List[str]:
        """获取建议"""
        recommendations = []
        if "token" in self.dynamic_fields:
            recommendations.append("建议参数化: token (通过CLI参数传入)")
        if "timestamp" in self.dynamic_fields:
            recommendations.append("建议参数化: timestamp (自动生成)")
        if "session" in self.dynamic_fields:
            recommendations.append("建议参数化: session (从Cookie提取)")
        return recommendations


def main():
    import sys
    if len(sys.argv) < 2:
        print("用法: python analyzer.py <recording.json>")
        sys.exit(1)
    
    analyzer = DynamicFieldAnalyzer(sys.argv[1])
    report = analyzer.analyze()
    
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 测试analyzer**

```bash
cd cli-anything-web-plugin
# 创建测试数据
echo '{"http_requests":[{"url":"https://api.example.com?token=abc123","body":"{\"timestamp\":1234567890}"}]}' > /tmp/test.json
python -c "from scripts.action_recorder.analyzer import DynamicFieldAnalyzer; a = DynamicFieldAnalyzer('/tmp/test.json'); print(a.analyze())"
```

Expected: 输出包含token和timestamp的dynamic_fields

- [ ] **Step 3: Commit**

```bash
git add cli-anything-web-plugin/scripts/action-recorder/analyzer.py
git commit -m "feat(action-recorder): add dynamic field analyzer

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 5: 实现重放代码生成器

**Files:**
- Create: `cli-anything-web-plugin/scripts/action-recorder/generator.py`

- [ ] **Step 1: 创建generator.py**

```python
"""生成重放代码 - 将录制数据转换为可执行的httpx调用"""

import json
import re
from typing import Dict, List, Set
from pathlib import Path


class ReplayGenerator:
    """从录制数据生成可重放的Python代码"""
    
    def __init__(self, recording_path: str):
        self.recording_path = Path(recording_path)
        with open(recording_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.params: Set[str] = set()
    
    def generate(self, params: Dict[str, str] = None) -> str:
        """生成可执行的Python代码"""
        if params is None:
            params = {}
        self.params = set(params.keys())
        
        return self._generate_code(params)
    
    def _generate_code(self, params: Dict[str, str]) -> str:
        """生成Python代码"""
        requests = self.data.get("http_requests", [])
        
        if not requests:
            return "# No HTTP requests recorded"
        
        # 只处理第一个请求作为demo
        req = requests[0]
        
        url = self._process_url(req.get("url", ""), params)
        method = req.get("method", "GET")
        headers = req.get("headers", {})
        body = req.get("body")
        
        code = f'''#!/usr/bin/env python3
"""自动生成的重放脚本 - 基于录制数据"""

import httpx
import json
from datetime import datetime

# 配置
BASE_URL = "{url.split("?")[0]}"
TIMEOUT = 30.0

def replay({self._generate_params_signature(params)}):
    """执行重放"""
    headers = {json.dumps(headers, indent=6)}
    
    # 替换动态参数
{self._generate_param_replacements(params)}
    
    url = f"{url.split("?")[0]}"
    
    try:
        response = httpx.{method}(url, headers=headers{", json=body_payload" if body and method in ["POST", "PUT", "PATCH"] else ""}, timeout=TIMEOUT)
        print(json.dumps({{
            "status": response.status_code,
            "body": response.text[:1000]
        }}, indent=2))
    except Exception as e:
        print(json.dumps({{"error": str(e)}}, indent=2))

if __name__ == "__main__":
    replay({self._generate_call_args(params)})
'''
        return code
    
    def _process_url(self, url: str, params: Dict[str, str]) -> str:
        """处理URL，替换动态参数"""
        for param in self.params:
            placeholder = f"{{{{{param}}}}}"
            if placeholder in url:
                url = url.replace(placeholder, params.get(param, ""))
        return url
    
    def _generate_params_signature(self, params: Dict[str, str]) -> str:
        """生成函数参数签名"""
        if not params:
            return ""
        return ", ".join([f'{k}="{v}"' for k, v in params.items()])
    
    def _generate_param_replacements(self, params: Dict[str, str]) -> str:
        """生成参数替换代码"""
        if not params:
            return "    pass"
        lines = []
        for key in params.keys():
            lines.append(f'    headers["{key}"] = {key}')
        return "\n".join(lines)
    
    def _generate_call_args(self, params: Dict[str, str]) -> str:
        """生成函数调用参数"""
        if not params:
            return ""
        return ", ".join([f'{k}={k}' for k in params.keys()])


def main():
    import sys
    if len(sys.argv) < 2:
        print("用法: python generator.py <recording.json> [--params key=value ...]")
        sys.exit(1)
    
    recording = sys.argv[1]
    params = {}
    
    # 解析参数
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--params":
            i += 1
            while i < len(sys.argv) and "=" in sys.argv[i]:
                key, value = sys.argv[i].split("=", 1)
                params[key] = value
                i += 1
        else:
            i += 1
    
    generator = ReplayGenerator(recording)
    code = generator.generate(params)
    print(code)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 测试generator**

```bash
cd cli-anything-web-plugin
# 测试生成
python -c "
from scripts.action_recorder.generator import ReplayGenerator
import json
import tempfile
data = {'http_requests': [{'method': 'POST', 'url': 'https://api.example.com/submit', 'headers': {'Content-Type': 'application/json'}, 'body': '{\"token\": \"abc\"}'}]}
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump(data, f)
    gen = ReplayGenerator(f.name)
    print(gen.generate({'token': 'placeholder'}))
"
```

Expected: 输出Python代码

- [ ] **Step 3: Commit**

```bash
git add cli-anything-web-plugin/scripts/action-recorder/generator.py
git commit -m "feat(action-recorder): add replay code generator

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 6: 创建CLI入口和重放Skill

**Files:**
- Create: `cli-anything-web-plugin/action-replay.py`
- Create: `cli-anything-web-plugin/skills/action-replay/SKILL.md`

- [ ] **Step 1: 创建action-replay.py**

```python
#!/usr/bin/env python3
"""Action Replay CLI - 重放录制的HTTP请求"""

import click
import json
from pathlib import Path
from scripts.action_recorder.generator import ReplayGenerator
from scripts.action_recorder.analyzer import DynamicFieldAnalyzer


@click.command()
@click.argument("recording_file", type=click.Path(exists=True))
@click.option("--params", "-p", multiple=True, help="动态参数，格式: key=value")
@click.option("--generate-only", "-g", is_flag=True, help="只生成代码，不执行")
@click.option("--analyze", "-a", is_flag=True, help="分析录制文件中的动态字段")
def main(recording_file: str, params: tuple, generate_only: bool, analyze: bool):
    """重放录制的HTTP请求"""
    
    if analyze:
        analyzer = DynamicFieldAnalyzer(recording_file)
        report = analyzer.analyze()
        click.echo(json.dumps(report, indent=2, ensure_ascii=False))
        return
    
    # 解析参数
    param_dict = {}
    for param in params:
        if "=" in param:
            key, value = param.split("=", 1)
            param_dict[key] = value
    
    # 生成代码
    generator = ReplayGenerator(recording_file)
    code = generator.generate(param_dict)
    
    if generate_only:
        click.echo(code)
        return
    
    # 执行代码
    exec(compile(code, recording_file, "exec"))


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 创建skills/action-replay/SKILL.md**

```markdown
---
name: cli-anything-web:action-replay
description: 重放录制的HTTP请求
argument-hint: <recording.json> [--params key=value ...]
trigger: "重放", "replay", "回放"
version: 1.0.0
---

# Action Replay - 重放录制

## 目标

重放录制的HTTP请求，可以参数化动态字段。

## 前置条件

- [ ] 已完成录制的JSON文件
- [ ] 安装httpx: `pip install httpx`

## 使用方法

### 分析录制文件

```bash
python cli-anything-web-plugin/action-replay.py <recording.json> --analyze
```

### 生成重放代码

```bash
python cli-anything-web-plugin/action-replay.py <recording.json> --generate-only
```

### 执行重放

```bash
python cli-anything-web-plugin/action-replay.py <recording.json> --params token=xxx
```

## 参数说明

- `recording_file`: 录制生成的JSON文件
- `--params, -p`: 动态参数，可多次指定
- `--analyze, -a`: 分析动态字段
- `--generate-only, -g`: 只生成代码不执行
```

- [ ] **Step 3: Commit**

```bash
git add cli-anything-web-plugin/action-replay.py cli-anything-web-plugin/skills/action-replay/
git commit -m "feat(action-recorder): add action-replay CLI and skill

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## 验收标准检查

- [ ] Task 1: 创建项目结构和基础模块
- [ ] Task 2: 完善HTTP请求捕获
- [ ] Task 3: 创建录制命令和Skill
- [ ] Task 4: 实现动态字段分析器
- [ ] Task 5: 实现重放代码生成器
- [ ] Task 6: 创建CLI入口和重放Skill

---

## 执行选项

**Plan complete and saved to `docs/superpowers/plans/2026-04-02-action-recorder.md`. Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**