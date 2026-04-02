# Publishing the cli-anything-web Plugin

This guide explains how to make the cli-anything-web plugin installable and how to
publish generated `cli-web-*` CLIs.

## Option 1: Local Installation (Development)

### For Testing

1. **Copy to Claude Code plugins directory:**
   ```bash
   cp -r /path/to/cli-anything-web-plugin ~/.claude/plugins/cli-anything-web
   ```

2. **Reload plugins in Claude Code:**
   ```bash
   /reload-plugins
   ```

3. **Verify installation:**
   ```bash
   /help cli-anything-web
   ```

### For Sharing Locally

```bash
tar -czf cli-anything-web-plugin-v0.1.0.tar.gz cli-anything-web-plugin/
```

Others can install:
```bash
cd ~/.claude/plugins
tar -xzf cli-anything-web-plugin-v0.1.0.tar.gz
```

## Option 2: GitHub Repository (Recommended)

```bash
cd cli-anything-web-plugin
git init
git add .
git commit -m "Initial commit: cli-anything-web plugin v0.1.0"
gh repo create cli-anything-web-plugin --public --source=. --remote=origin
git push -u origin main
```

Users can install directly:
```bash
cd ~/.claude/plugins
git clone https://github.com/yourusername/cli-anything-web-plugin.git cli-anything-web
```

---

# Publishing Generated CLIs

After generating a CLI with `/cli-anything-web <url>`, you can publish it for others to use.

## Package structure (PEP 420 namespace)

```
<app>/agent-harness/
├── setup.py
└── cli_web/              # NO __init__.py (namespace package)
    └── <app>/            # HAS __init__.py
        ├── <app>_cli.py
        ├── core/
        └── tests/
```

### setup.py template

```python
from setuptools import setup, find_namespace_packages

setup(
    name="cli-web-<app>",
    version="1.0.0",
    packages=find_namespace_packages(include=["cli_web.*"]),
    install_requires=[
        "click>=8.0.0",
        "httpx>=0.24.0",
        "prompt-toolkit>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "cli-web-<app>=cli_web.<app>.<app>_cli:main",
        ],
    },
    python_requires="">=3.10",
)
```

Key rules:
- Use `find_namespace_packages`, NOT `find_packages`
- Use `include=["cli_web.*"]` to scope discovery
- Entry point: `cli_web.<app>.<app>_cli:main`

### Install and test locally

```bash
cd <app>/agent-harness
pip install -e .
which cli-web-<app>
cli-web-<app> --help
CLI_WEB_FORCE_INSTALLED=1 python3 -m pytest cli_web/<app>/tests/ -v -s
```

---

## Publishing to PyPI

### Standard PyPI

```bash
pip install build twine
python -m build
twine upload dist/*
```

Users install with:
```bash
pip install cli-web-<app>
cli-web-<app> --help
```

### 海尔内网 PyPI 私服

如果需要发布到海尔内部 PyPI 私服：

#### 1. 配置 pip（用户需要先配置）

编辑 `~/.pip/pip.conf`（Linux/Mac）或 `%USERPROFILE%\pip\pip.ini`（Windows）：

```ini
[global]
index-url = https://pipstore.haier.net/repository/pypi-all/simple
```

#### 2. 发布包

```bash
# 构建包
pip install build
python -m build

# 上传到海尔 PyPI（每次可能使用不同的 S 码）
twine upload --repository-url https://pipstore.haier.net/repository/<S码>/ -u <S码用户名> -p <S码密码> dist/*
```

**注意**：
- `<S码>` 由管理员分配，每个开发者可能不同
- 上传前需要联系管理员获取 S 码账号
- 如果遇到 401 错误，检查用户名和密码是否正确

#### 3. 用户安装

```bash
# 方法一：配置 pip.conf（推荐，一劳永逸）
pip install cli-web-<app>

# 方法二：临时指定源
pip install cli-web-<app> -i https://pipstore.haier.net/repository/pypi-all/simple
```

---

## 生成并分发 Skill

生成 CLI 后，还需要创建 skill 方便用户在 Claude Code 中使用。

### 1. 创建 skill 目录结构

```
项目目录/.claude/skills/<app>-cli/
└── SKILL.md
```

### 2. SKILL.md 模板

```markdown
---
name: {{app}}-cli
description: Use cli-web-{{app}} to {{one_line_purpose}}. Invoke this skill whenever
  the user asks about {{trigger_topics}}. Always prefer cli-web-{{app}} over manually
  fetching the website.
---

# cli-web-{{app}}

{{one_sentence_description}}. Installed at: `cli-web-{{app}}`.

## 首次使用？先安装 CLI

### 海尔内网（推荐）

```bash
# 配置 pip（如未配置）
# Windows: %USERPROFILE%\pip\pip.ini
# Linux/Mac: ~/.pip/pip.conf
[global]
index-url = https://pipstore.haier.net/repository/pypi-all/simple

# 安装 CLI
pip install cli-web-{{app}}
```

或开发版安装：

```bash
pip install -e /path/to/{{app}}/agent-harness
```

安装完成后重启 Claude Code 即可使用。

---

## Quick Start

```bash
# {{most_common_operation_description}}
cli-web-{{app}} {{primary_command}} --json

# {{second_operation_description}}
cli-web-{{app}} {{secondary_command}} --json
```

Always use `--json` when parsing output programmatically.

---

## Commands

{{FOR_EACH_COMMAND_GROUP}}
### `{{group}} {{verb}}`
{{command_description}}

```bash
cli-web-{{app}} {{group}} {{verb}} [options] --json
```

**Key options:** {{options_list}}
**Output fields:** {{json_fields}}
{{END_FOR_EACH}}

---

## Notes

- Auth: {{auth_description}}
- Rate limiting: {{rate_limit_notes}}
```

### 3. 分发给用户

用户需要做两件事：

1. **复制 skill 文件**到 `~/.claude/skills/<app>-cli/SKILL.md`
2. **安装 CLI**：`pip install cli-web-<app>`

---

## 完整发布流程

1. **生成 CLI**：使用 `/cli-anything-web <url>` 生成 CLI 代码

2. **本地测试**：
   ```bash
   cd <app>/agent-harness
   pip install -e .
   cli-web-<app> --help
   ```

3. **构建包**：
   ```bash
   python -m build
   ```

4. **发布 CLI**（二选一）：
   - 标准 PyPI：`twine upload dist/*`
   - 海尔私服：`twine upload --repository-url https://pipstore.haier.net/repository/<S码>/ ...`

5. **创建 skill**：
   - 在项目目录创建 `.claude/skills/<app>-cli/SKILL.md`
   - 填充模板内容，添加安装说明

6. **分发**：
   - 提供 skill 文件给用户
   - 提供安装命令：`pip install cli-web-<app>`

---

## Versioning

Follow semantic versioning:
- **Major**: Breaking API changes
- **Minor**: New commands, backward compatible
- **Patch**: Bug fixes

Update version in `setup.py` and git tags.

## Distribution Checklist

Before publishing:

- [ ] All commands tested and working
- [ ] README.md is comprehensive
- [ ] LICENSE file included
- [ ] setup.py has correct namespace config
- [ ] No hardcoded credentials or tokens
- [ ] Tests pass (unit + E2E)
- [ ] `cli-web-<app> --help` shows all commands
- [ ] `cli-web-<app> --json <cmd>` works
- [ ] SKILL.md created with installation instructions