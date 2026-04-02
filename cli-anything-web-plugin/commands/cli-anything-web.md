---
name: cli-anything-web
description: Generate a complete agent-native CLI for any web app by recording and analyzing network traffic via playwright-cli. Runs the full pipeline with site assessment, capture, implementation, testing, and verification.
argument-hint: <url> [--mitmproxy]
allowed-tools: Bash(*), Read, Write, Edit, mcp__chrome-devtools__*
---

# CLI-Anything-Web: Full Pipeline

Read the methodology overview:
@${CLAUDE_PLUGIN_ROOT}/HARNESS.md

Target URL and flags: $ARGUMENTS

## Scope Confirmation (IMPORTANT)

Extract the app name from the URL (e.g., `https://iac.haier.net/Initiate?id=...` → domain: `haier.net`).

**Before starting capture, ask the user to confirm scope:**

```
我检测到你要为以下网站生成 CLI：
- URL: <url>
- 应用名: <app>

这个 URL 是一个特定页面还是整个网站？
- [1] 整个网站 (默认) - 探索所有功能，生成完整 CLI
- [2] 特定页面/功能 - 只抓取这个页面的 API
- [3] 取消
```

根据用户选择设置抓取范围：
- **选项 1 (整个网站)**: 执行标准全站抓取流程
- **选项 2 (特定页面)**: 只抓取当前 URL 的 API，然后停止抓取，生成的 CLI 会标记为"简化版"
- **选项 3**: 礼貌退出

**保存用户选择到 phase state:**
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/phase-state.py update <app> --phase capture --data "scope=<full|partial>"
```

## Capture Mode Detection

Check if `--mitmproxy` flag is present in the arguments:
- **With `--mitmproxy`**: Use mitmproxy-capture.py for traffic capture (no body truncation, real-time filtering, enhanced analysis). Requires `pip install mitmproxy` (Python 3.12+).
- **Without `--mitmproxy`** (default): Use standard playwright-cli tracing (the original method).

## Prerequisites Check

### Step 1: Check playwright-cli availability
!`npx @playwright/cli@latest --version 2>&1 && echo "PLAYWRIGHT_OK" || echo "PLAYWRIGHT_FAIL"`

**If PLAYWRIGHT_OK** → use playwright-cli for all operations (primary path).

**If PLAYWRIGHT_FAIL** → If playwright-cli is not available, see HARNESS.md for the MCP fallback path.

### Step 1b: If `--mitmproxy` flag was passed, also verify mitmproxy
!`python -c "import mitmproxy; print('MITMPROXY_OK')" 2>&1 || echo "MITMPROXY_FAIL"`

**If MITMPROXY_FAIL** → Tell user to `pip install mitmproxy` or drop the `--mitmproxy` flag.

### NEVER use `mcp__claude-in-chrome__*` tools -- blocked, cannot capture request bodies.

## Execution Plan

Run the full pipeline by invoking skills in sequence. **Each phase checks for
prior completion and skips if already done.**

1. Check playwright-cli availability (see Prerequisites above)
2. **Check pipeline state:** `python ${CLAUDE_PLUGIN_ROOT}/scripts/phase-state.py status <app>`
   - If a phase is already `done` → skip it and proceed to the next
   - If a phase `failed` with `retryable` → retry automatically
   - If a phase `failed` with `fatal` → report and ask user
3. For each phase, check before running:
   ```bash
   python ${CLAUDE_PLUGIN_ROOT}/scripts/phase-state.py check <app> --phase <phase>
   # Exit 0 = skip (already done), Exit 1 = run
   ```
4. **Check scope from phase-state:**
   ```bash
   python ${CLAUDE_PLUGIN_ROOT}/scripts/phase-state.py get <app> --key scope
   ```
   - If `scope=partial`: 告诉 capture skill 只抓取当前页面，不探索其他页面
   - If `scope=full` 或未设置: 执行标准全站抓取
5. Invoke `capture` skill -- Phase 1 site assessment + traffic recording
   - Also check capture checkpoint: `python ${CLAUDE_PLUGIN_ROOT}/scripts/capture-checkpoint.py restore <app>`
   - **重要**: 如果 `scope=partial`，只抓取用户提供的 URL，不进行站点探索
6. Invoke `methodology` skill -- Phase 2 analyze/design/implement
   - Agent MUST read a reference CLI first (same protocol) — see methodology skill
   - **重要**: 如果 `scope=partial`，在 APP.md 中标记为"简化版 CLI"并只实现当前页面的功能
7. Invoke `testing` skill -- Phase 3 test writing/documentation
8. Invoke `standards` skill -- Phase 4 publish and verify + generate Claude skill

After each phase completes, mark it:
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/phase-state.py complete <app> --phase <phase> --output <output-path>
```

Each skill handles its phases completely and invokes the next when done.
See HARNESS.md for the pipeline overview and critical rules.

Extract the app name from the URL (e.g., `monday.com` → `monday`, `notion.so` → `notion`).

## Success Criteria

The command succeeds when:
1. All core modules are implemented and functional (`client.py`, `auth.py`, `session.py`, `models.py`)
2. CLI supports both one-shot commands and REPL mode
3. `--json` output mode works for all commands
4. All tests pass (100% pass rate)
5. Subprocess tests use `_resolve_cli()` and pass with `CLI_WEB_FORCE_INSTALLED=1`
6. TEST.md contains both plan (Part 1) and results (Part 2)
7. README.md documents installation and usage
8. `setup.py` is created and local installation works
9. CLI is available in PATH as `cli-web-<app>`
10. `.claude/skills/<app>-cli/SKILL.md` exists at the project root

## Output Structure

```
<app-name>/
└── agent-harness/
    ├── <APP>.md               # API map, data model, auth scheme
    ├── setup.py               # PyPI config (find_namespace_packages)
    └── cli_web/               # Namespace package (NO __init__.py)
        └── <app>/             # Sub-package
            ├── __init__.py    # Required — marks as sub-package
            ├── README.md
            ├── <app>_cli.py   # Main CLI entry point
            ├── __main__.py
            ├── core/
            │   ├── client.py
            │   ├── auth.py
            │   ├── session.py
            │   └── models.py
            ├── utils/
            │   ├── repl_skin.py
            │   ├── output.py
            │   └── config.py
            └── tests/
                ├── TEST.md
                ├── test_core.py
                └── test_e2e.py
```

**No-auth sites:** Remove `core/auth.py`, `core/session.py`, and auth commands
from the structure above. Only create what the CLI actually needs.

## Progress Tracking

After each phase, report status in this format:

```
┌─────────┬────────┬────────────────────────────────────────────┐
│ Phase   │ Status │ Description                                │
├─────────┼────────┼────────────────────────────────────────────┤
│ Phase 1 │ ...    │ Capture — Traffic Capture + Auth           │
│ Phase 2 │ ...    │ Methodology — Analyze + Design + Implement │
│ Phase 3 │ ...    │ Test — Write Tests + Document Results      │
│ Phase 4 │ ...    │ Standards — Publish + Smoke Test + Skill   │
└─────────┴────────┴────────────────────────────────────────────┘
```
