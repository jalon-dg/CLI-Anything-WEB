# Plugin Agents & Skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add 4 review agents, 1 boilerplate skill, 1 consistency checker agent, and 1 gap analyzer skill to the cli-anything-web plugin.

**Architecture:** New files go in `cli-anything-web-plugin/agents/` and `cli-anything-web-plugin/skills/`. Three existing files get surgical edits. One reference file gets deleted after migration.

**Tech Stack:** Claude Code plugin system (markdown frontmatter agents + skills)

**Spec:** `docs/superpowers/specs/2026-03-27-plugin-agents-skills-design.md`

---

## File Map

### New Files
| File | Responsibility |
|------|---------------|
| `cli-anything-web-plugin/agents/traffic-fidelity-reviewer.md` | Review agent: API map vs code fidelity |
| `cli-anything-web-plugin/agents/harness-compliance-reviewer.md` | Review agent: HARNESS convention compliance |
| `cli-anything-web-plugin/agents/output-ux-reviewer.md` | Review agent: UX, help, JSON output quality |
| `cli-anything-web-plugin/agents/cross-cli-consistency-checker.md` | Audit agent: convention drift across all CLIs |
| `cli-anything-web-plugin/skills/boilerplate/SKILL.md` | Skill: scaffold core/ modules from protocol type |
| `cli-anything-web-plugin/skills/gap-analyzer/SKILL.md` | Skill: structured gap analysis for refine |

### Modified Files
| File | Change |
|------|--------|
| `cli-anything-web-plugin/skills/standards/SKILL.md` | Replace lines 54-55 (agent dispatch instruction) |
| `cli-anything-web-plugin/skills/methodology/SKILL.md` | Insert Step B.0 between lines 167-169 |
| `cli-anything-web-plugin/commands/refine.md` | Replace step 3 (lines 26-29) with gap-analyzer invocation |

### Deleted Files
| File | Reason |
|------|--------|
| `cli-anything-web-plugin/skills/standards/references/review-agents.md` | Content migrated to 3 agent files |

---

## Task 1: Traffic Fidelity Reviewer Agent

**Files:**
- Create: `cli-anything-web-plugin/agents/traffic-fidelity-reviewer.md`

- [ ] **Step 1: Create the agents directory**

```bash
mkdir -p cli-anything-web-plugin/agents
```

- [ ] **Step 2: Write the traffic fidelity reviewer agent**

Create `cli-anything-web-plugin/agents/traffic-fidelity-reviewer.md` with this exact content:

```markdown
---
name: traffic-fidelity-reviewer
version: 0.1.0
description: >
  Review a cli-web-* CLI implementation against its <APP>.md API map.
  Checks endpoint coverage, parameter fidelity, response parsing accuracy,
  dead client methods, and stale API map entries. Returns scored findings.
  Use during Phase 4 standards review — dispatched by the standards skill.
tools: [Read, Grep, Glob]
---

# Traffic Fidelity Reviewer

You are reviewing a generated CLI to verify it faithfully implements the
API surface discovered during traffic capture.

**Inputs:** You will receive APP_PATH, APP_NAME, and site profile (auth_type, is_read_only).

## Site Profile Awareness

Before scoring, determine the site profile:
- **No-auth sites**: Skip all auth-related checks (auth.py, auth commands,
  cookie priority, auth retry). Do NOT report missing auth features as findings.
- **Read-only sites**: Skip write operation checks.
- **No-RPC sites**: Skip batchexecute/RPC-specific checks.

Mark skipped checks as N/A, not as findings.

## Scope Boundary

You own: API map vs code fidelity ONLY.
Do NOT report code quality issues (that's harness-compliance-reviewer).
Do NOT report UX issues (that's output-ux-reviewer).

## Your Task

1. Read `{APP_PATH}/agent-harness/{APP_UPPER}.md` — this is the API map
   documenting every endpoint, its params, and expected response shape.
2. Read `{APP_PATH}/agent-harness/cli_web/{app}/core/client.py` — the HTTP
   client that implements each endpoint.
3. Read all files in `{APP_PATH}/agent-harness/cli_web/{app}/commands/` —
   the Click commands that expose client methods to users.
4. Compare what the API map documents vs what the code implements.

## What to Check

**Endpoint Coverage:**
- Every endpoint in the API map has a corresponding client method
- No client methods exist for undocumented endpoints (possible hallucination)
- No dead client methods (implemented but never called by any command)
- HTTP method (GET/POST) matches the API map
- API map (`<APP>.md`) matches actual implementation (not stale from initial traffic capture)

**Parameter Fidelity:**
- Required params from the API map are passed in client methods
- Query params, form data, and headers match the documented format
- No hardcoded values that should be dynamic (session IDs, CSRF tokens, build labels)

**Response Parsing:**
- Client methods extract the fields documented in the API map
- Nested data structures are traversed correctly
- Normalizer functions produce the fields that commands expect
- No fields are silently dropped that the API map documents

**Command Surface:**
- Every client method is exposed through a Click command
- Command arguments/options match the client method parameters
- `--json` flag is present on every command

## Output Format

Return a list of findings, each with:
- **confidence**: 0-100 score
- **severity**: Critical / Important / Minor
- **file**: path:line
- **description**: What's wrong
- **evidence**: The specific mismatch (API map says X, code does Y)
```

- [ ] **Step 3: Verify the file was created correctly**

```bash
head -5 cli-anything-web-plugin/agents/traffic-fidelity-reviewer.md
```
Expected: frontmatter with `name: traffic-fidelity-reviewer`

---

## Task 2: HARNESS Compliance Reviewer Agent

**Files:**
- Create: `cli-anything-web-plugin/agents/harness-compliance-reviewer.md`

- [ ] **Step 1: Write the harness compliance reviewer agent**

Create `cli-anything-web-plugin/agents/harness-compliance-reviewer.md` with this exact content:

```markdown
---
name: harness-compliance-reviewer
version: 0.1.0
description: >
  Review a cli-web-* CLI for HARNESS.md convention compliance.
  Checks exception hierarchy, auth patterns, client architecture,
  CLI patterns (UTF-8, shlex, handle_errors), and JSON output format.
  Returns scored findings. Use during Phase 4 standards review.
tools: [Read, Grep, Glob]
---

# HARNESS Compliance Reviewer

You are reviewing a generated CLI to verify it follows all HARNESS.md
conventions and the quality checklist — not just structurally, but in
actual code logic.

**Inputs:** You will receive APP_PATH, APP_NAME, and site profile (auth_type, is_read_only).

## Site Profile Awareness

Before scoring, determine the site profile:
- **No-auth sites**: Skip all auth-related checks (auth.py, auth commands,
  cookie priority, auth retry). Do NOT report missing auth features as findings.
- **Read-only sites**: Skip write operation checks.
- **No-RPC sites**: Skip batchexecute/RPC-specific checks.

Mark skipped checks as N/A, not as findings.

## Scope Boundary

You own: code quality and HARNESS conventions ONLY.
Do NOT report API coverage issues (that's traffic-fidelity-reviewer).
Do NOT report UX/output issues (that's output-ux-reviewer).

## Your Task

1. Find and read HARNESS.md by globbing for `**/cli-anything-web-plugin/HARNESS.md`.
2. Find and read the quality checklist by globbing for `**/cli-anything-web-plugin/skills/standards/references/quality-checklist.md`.
3. Read all source files in `{APP_PATH}/agent-harness/cli_web/{app}/`.
4. Check each applicable convention against the actual implementation.

## What to Check

**Exception Hierarchy (core/exceptions.py):**
- `AppError` base class exists with `to_dict()` method
- All required subtypes: `AuthError`, `RateLimitError`, `NetworkError`,
  `ServerError`, `NotFoundError`
- `AuthError` has `recoverable` flag (skip for no-auth sites if class exists as boilerplate)
- `RateLimitError` has `retry_after` field AND `to_dict()` includes it in output
- `ServerError` stores `status_code` as instance attribute
- Error codes match HARNESS.md: `AUTH_EXPIRED`, `RATE_LIMITED`, `NETWORK_ERROR`, `SERVER_ERROR`, `NOT_FOUND`
- Client maps HTTP status codes correctly (401→AuthError, 404→NotFoundError,
  429→RateLimitError, 5xx→ServerError)

**Auth (core/auth.py, core/client.py) — SKIP for no-auth sites:**
- Credentials stored with `chmod 600`
- `CLI_WEB_{APP}_AUTH_JSON` env var supported
- Client retries ONCE on recoverable AuthError (not more)
- Google cookie domain priority (`.google.com` over regional ccTLDs)
- `load_cookies()` handles both list format and dict format

**Client Architecture (core/client.py):**
- Centralized auth header injection
- Exponential backoff for polling (2s→10s, factor 1.5) — not fixed sleep
- Rate-limit retry on 429
- No bare `except:` blocks
- No hardcoded tokens, URLs, or session IDs

**CLI Patterns (<app>_cli.py):**
- `invoke_without_command=True` for REPL default
- UTF-8 fix for BOTH `sys.stdout` AND `sys.stderr` on Windows
- `shlex.split()` in REPL (not `line.split()`)
- `cli.main(args=..., standalone_mode=False)` for REPL dispatch
- Commands use `handle_errors()` context manager — no manual try/except

**JSON Output:**
- Success: `{"success": true, "data": {...}}`
- Error: `{"error": true, "code": "...", "message": "..."}`
- No raw protocol data in output (no `wrb.fr`, `af.httprm`, empty `[]`)
- **RED FLAG: `click.ClickException`** — if any command raises `click.ClickException`
  instead of a typed domain exception, it bypasses `handle_errors()` and produces
  non-structured error output in `--json` mode. This is a common bug in submit/comment
  commands where Reddit API errors are caught from the response JSON.

**Base Exception Class:**
- Must have `to_dict()` method returning `{"error": True, "code": "...", "message": "..."}`
- `RateLimitError.to_dict()` must include `retry_after`
- `ServerError` must store `status_code` as instance attribute

## Output Format

Return a list of findings, each with:
- **confidence**: 0-100 score
- **severity**: Critical / Important / Minor
- **file**: path:line
- **description**: What's wrong
- **evidence**: The specific mismatch (convention says X, code does Y)
```

- [ ] **Step 2: Verify the file**

```bash
head -5 cli-anything-web-plugin/agents/harness-compliance-reviewer.md
```

---

## Task 3: Output & UX Reviewer Agent

**Files:**
- Create: `cli-anything-web-plugin/agents/output-ux-reviewer.md`

- [ ] **Step 1: Write the output UX reviewer agent**

Create `cli-anything-web-plugin/agents/output-ux-reviewer.md` with this exact content:

```markdown
---
name: output-ux-reviewer
version: 0.1.0
description: >
  Review a cli-web-* CLI from the end-user perspective.
  Checks --help completeness, REPL help sync, JSON output quality,
  protocol leak detection, and entry point correctness.
  Returns scored findings. Use during Phase 4 standards review.
tools: [Read, Grep, Glob, Bash]
---

# Output & UX Reviewer

You are reviewing a generated CLI from the end-user perspective — does
it work correctly, is help complete, is output clean?

**Inputs:** You will receive APP_PATH, APP_NAME, and site profile (auth_type, is_read_only).

## Site Profile Awareness

Before scoring, determine the site profile:
- **No-auth sites**: Skip auth command checks. Do NOT report missing auth help as findings.
- **Read-only sites**: Skip write command checks.
- **No-RPC sites**: Skip batchexecute/RPC-specific output checks.

Mark skipped checks as N/A, not as findings.

## Scope Boundary

You own: user-facing behavior ONLY.
Do NOT report API coverage issues (that's traffic-fidelity-reviewer).
Do NOT report code quality issues (that's harness-compliance-reviewer).

## Your Task

1. Run `cli-web-{app} --help` and capture output.
2. Run each subcommand group's `--help` (e.g., `feed --help`, `search --help`).
3. Read `_print_repl_help()` in `{app}_cli.py` and compare against actual commands.
4. If auth is available, run a few commands with `--json` and inspect output.
5. Read `setup.py` and verify entry point matches CLI name.

## What to Check

**Help Completeness:**
- `--help` lists all command groups
- Each group's `--help` lists all subcommands
- Arguments and options have help text
- REPL `help` output matches the actual command surface (no missing commands,
  no stale entries)
- No command files in `commands/` that are not registered on the CLI group
  (dead files that would crash if imported)

**JSON Output Quality:**
- Commands return valid JSON (parseable by `json.loads`)
- No raw protocol artifacts leak through (search for: `wrb.fr`, `af.httprm`,
  `[[`, `null`, empty strings where data should be)
- Error responses follow structured format
- Pagination cursors are exposed (`"after": "..."`)

**Entry Point:**
- `setup.py` console_scripts entry matches `cli-web-{app}`
- `__main__.py` has `if __name__` guard
- Package name follows `cli-web-{app}` convention

**REPL Quality:**
- REPL banner shows app name and version
- REPL prompt is distinctive (not generic `>`)
- `help` command works
- `quit`/`exit` commands work
- Arrow keys / history work (prompt_toolkit)

## Output Format

Return a list of findings, each with:
- **confidence**: 0-100 score
- **severity**: Critical / Important / Minor
- **file**: path:line
- **description**: What's wrong
- **evidence**: The specific mismatch or actual output snippet
```

- [ ] **Step 2: Verify the file**

```bash
head -5 cli-anything-web-plugin/agents/output-ux-reviewer.md
```

---

## Task 4: Update Standards Skill + Delete Old Reference

**Files:**
- Modify: `cli-anything-web-plugin/skills/standards/SKILL.md` (lines 54-55)
- Delete: `cli-anything-web-plugin/skills/standards/references/review-agents.md`

- [ ] **Step 1: Update the standards skill dispatch instruction**

In `cli-anything-web-plugin/skills/standards/SKILL.md`, replace lines 54-55:

Old text:
```
Dispatch 3 agents in the **same message** using the Agent tool. Read the
complete agent prompts from `references/review-agents.md`.
```

New text:
```
Dispatch 3 plugin agents in the **same message** using the Agent tool:
- `traffic-fidelity-reviewer` — API coverage (reads <APP>.md + client.py + commands/)
- `harness-compliance-reviewer` — Code conventions (reads HARNESS.md + all source)
- `output-ux-reviewer` — User experience (runs --help, checks REPL, validates JSON)

Pass each agent: APP_PATH=`{app}/agent-harness`, APP_NAME=`{app}`, and site
profile (auth_type, is_read_only). The agents are defined in the plugin's
`agents/` directory.
```

- [ ] **Step 2: Verify the edit**

```bash
sed -n '49,80p' cli-anything-web-plugin/skills/standards/SKILL.md
```
Expected: new dispatch text with 3 agent bullet points

- [ ] **Step 3: Delete the old review-agents.md reference file**

```bash
rm cli-anything-web-plugin/skills/standards/references/review-agents.md
```

- [ ] **Step 4: Verify deletion**

```bash
ls cli-anything-web-plugin/skills/standards/references/
```
Expected: `quality-checklist.md` only (review-agents.md gone)

- [ ] **Step 5: Commit review agents + standards update**

```bash
git add cli-anything-web-plugin/agents/ cli-anything-web-plugin/skills/standards/
git commit -m "feat(plugin): add 3 review agents, replace review-agents.md reference

Migrate Traffic Fidelity, HARNESS Compliance, and Output & UX review
prompts from references/review-agents.md into proper plugin agent files.
Update standards skill Step 1 to dispatch agents by name.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: Boilerplate Generator Skill

**Files:**
- Create: `cli-anything-web-plugin/skills/boilerplate/SKILL.md`
- Modify: `cli-anything-web-plugin/skills/methodology/SKILL.md` (insert after line 167)

- [ ] **Step 1: Create the boilerplate skill directory**

```bash
mkdir -p cli-anything-web-plugin/skills/boilerplate
```

- [ ] **Step 2: Write the boilerplate generator skill**

Create `cli-anything-web-plugin/skills/boilerplate/SKILL.md`. This is the largest file — it contains input collection, decision matrix, and code templates for each generated file.

The skill should contain:

```markdown
---
name: boilerplate
version: 0.1.0
description: >
  Generate core/ module scaffolds (exceptions.py, client.py, helpers.py, config.py)
  from protocol type, auth type, and resource list. Reduces Phase 2 setup from
  hours to minutes. TRIGGER: automatically during Phase 2 Step B.0 when the
  methodology skill instructs to scaffold core modules. DO NOT trigger for:
  traffic capture, test writing, or quality checks.
user-invocable: false
---

# Boilerplate Generator

Generate the foundational core/ modules for a new cli-web-* CLI. This skill
is invoked during Phase 2 (methodology) Step B.0, after traffic analysis and
command structure design are complete.

---

## Step 1: Collect Inputs

Read `traffic-analysis.json` in `{app}/traffic-capture/` to extract:

| Parameter | Source | Example |
|-----------|--------|---------|
| `app_name` | Directory name | `hackernews` |
| `APP_NAME` | Uppercase | `HACKERNEWS` |
| `AppName` | PascalCase | `HackerNews` |
| `protocol` | `traffic-analysis.json` → `protocol_type` | `rest` |
| `http_client` | `traffic-analysis.json` → `protection` field | `httpx` or `curl_cffi` |
| `auth_type` | `traffic-analysis.json` → `auth_pattern` | `none`, `cookie`, `google-sso`, `api-key` |
| `resources` | `<APP>.md` → endpoint groups | `["stories", "search", "user"]` |
| `has_polling` | Any generation/async endpoints? | `false` |
| `has_context` | Multi-resource app with `use <id>`? | `false` |
| `has_partial_ids` | UUID-based entity IDs? | `false` |

**Fallback:** If `traffic-analysis.json` doesn't exist, derive parameters from `<APP>.md` header section.

---

## Step 2: Decision Matrix

| Parameter | Affects |
|-----------|---------|
| `protocol` | client.py structure (REST vs GraphQL vs batchexecute vs HTML) |
| `http_client` | Import line in client.py (`httpx` vs `curl_cffi`) |
| `auth_type` | Whether config.py includes auth paths; `none` = no auth files at all |
| `has_polling` | Whether helpers.py includes `poll_until_complete()` |
| `has_context` | Whether helpers.py includes `get/set_context_value()`, `require_*()` |
| `has_partial_ids` | Whether helpers.py includes `resolve_partial_id()` |

### Files to Generate

| File | Condition |
|------|-----------|
| `core/__init__.py` | Always (empty) |
| `core/exceptions.py` | Always |
| `core/config.py` | Always |
| `core/client.py` | Always |
| `core/rpc/__init__.py` | protocol = batchexecute |
| `core/rpc/types.py` | protocol = batchexecute |
| `core/rpc/encoder.py` | protocol = batchexecute |
| `core/rpc/decoder.py` | protocol = batchexecute |
| `utils/__init__.py` | Always (empty) |
| `utils/helpers.py` | Always |
| `utils/output.py` | Always |
| `__init__.py` | Always |
| `__main__.py` | Always |

---

## Step 3: Generate Files

### 3.1: `__init__.py`

```python
"""cli-web-{app_name} — CLI for {app_name}."""

__version__ = "0.1.0"
```

### 3.2: `__main__.py`

```python
"""Allow running as: python -m cli_web.{app_name}"""
from cli_web.{app_name}.{app_name}_cli import cli

if __name__ == "__main__":
    cli()
```

### 3.3: `core/exceptions.py`

Generate the full exception hierarchy. This is identical across all CLIs
except for the base class name prefix:

```python
"""Typed exception hierarchy for cli-web-{app_name}."""


class {AppName}Error(Exception):
    """Base exception for all cli-web-{app_name} errors."""

    def to_dict(self):
        return {
            "error": True,
            "code": _error_code_for(self),
            "message": str(self),
        }


class AuthError({AppName}Error):
    """Authentication failed — expired cookies, invalid tokens."""

    def __init__(self, message: str, recoverable: bool = True):
        self.recoverable = recoverable
        super().__init__(message)


class RateLimitError({AppName}Error):
    """Server returned 429 — too many requests."""

    def __init__(self, message: str, retry_after: float | None = None):
        self.retry_after = retry_after
        super().__init__(message)

    def to_dict(self):
        d = super().to_dict()
        if self.retry_after is not None:
            d["retry_after"] = self.retry_after
        return d


class NetworkError({AppName}Error):
    """Connection failed — DNS, TCP, TLS."""


class ServerError({AppName}Error):
    """Server returned 5xx."""

    def __init__(self, message: str, status_code: int = 500):
        self.status_code = status_code
        super().__init__(message)


class NotFoundError({AppName}Error):
    """Resource not found (HTTP 404)."""


# --- Error code mapping ---

_CODE_MAP = {
    AuthError: "AUTH_EXPIRED",
    RateLimitError: "RATE_LIMITED",
    NotFoundError: "NOT_FOUND",
    ServerError: "SERVER_ERROR",
    NetworkError: "NETWORK_ERROR",
}


def _error_code_for(exc):
    for exc_type, code in _CODE_MAP.items():
        if isinstance(exc, exc_type):
            return code
    return "UNKNOWN_ERROR"


def raise_for_status(response) -> None:
    """Map HTTP status to typed exception."""
    sc = response.status_code
    if sc < 400:
        return
    text = getattr(response, "text", "")[:200]
    msg = f"HTTP {sc}: {text}"
    if sc in (401, 403):
        raise AuthError(msg, recoverable=True)
    if sc == 404:
        raise NotFoundError(msg)
    if sc == 429:
        retry_after = None
        if hasattr(response, "headers"):
            ra = response.headers.get("Retry-After")
            if ra:
                retry_after = float(ra)
        raise RateLimitError(msg, retry_after=retry_after)
    if 500 <= sc < 600:
        raise ServerError(msg, status_code=sc)
    raise {AppName}Error(msg)
```

### 3.4: `core/config.py`

```python
"""Configuration paths for cli-web-{app_name}."""
import os
from pathlib import Path

APP_NAME = "{app_name}"
CONFIG_DIR = Path.home() / ".config" / f"cli-web-{app_name}"
AUTH_FILE = CONFIG_DIR / "auth.json"
CONTEXT_FILE = CONFIG_DIR / "context.json"

# Environment variable override for CI/CD
AUTH_ENV_VAR = "CLI_WEB_{APP_NAME}_AUTH_JSON"


def get_auth_path() -> Path:
    """Return auth file path, preferring env var override."""
    env = os.environ.get(AUTH_ENV_VAR)
    if env:
        return Path(env)
    return AUTH_FILE
```

### 3.5: `core/client.py`

Generate based on `protocol` and `http_client`:

**If protocol = REST and http_client = httpx:**
```python
"""HTTP client for cli-web-{app_name}."""
import httpx
from .exceptions import AuthError, NetworkError, raise_for_status

class {AppName}Client:
    BASE_URL = "https://FIXME.example.com"  # TODO: Set from traffic capture

    def __init__(self, cookies: dict | None = None):
        self._cookies = cookies or {}
        self._client = httpx.Client(
            base_url=self.BASE_URL,
            timeout=httpx.Timeout(connect=10.0, read=30.0, write=30.0, pool=30.0),
            headers={"User-Agent": "cli-web-{app_name}/0.1.0"},
        )

    def _request(self, method: str, url: str, retry_auth: bool = True, **kwargs) -> httpx.Response:
        kwargs.setdefault("cookies", self._cookies)
        try:
            resp = self._client.request(method, url, **kwargs)
        except httpx.ConnectError as e:
            raise NetworkError(f"Connection failed: {e}")
        except httpx.TimeoutException as e:
            raise NetworkError(f"Request timed out: {e}")
        if resp.status_code in (401, 403) and retry_auth:
            self._refresh_auth()
            return self._request(method, url, retry_auth=False, **kwargs)
        raise_for_status(resp)
        return resp

    def _refresh_auth(self):
        raise AuthError("Auth expired. Run: cli-web-{app_name} auth login", recoverable=False)

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    # --- Endpoint methods (implement from <APP>.md) ---
    # def list_items(self, **params): ...
    # def get_item(self, item_id): ...
```

**If protocol = REST and http_client = curl_cffi:**
```python
"""HTTP client for cli-web-{app_name} (curl_cffi for anti-bot bypass)."""
from curl_cffi import requests as curl_requests
from .exceptions import AuthError, NetworkError, raise_for_status

class {AppName}Client:
    BASE_URL = "https://FIXME.example.com"  # TODO: Set from traffic capture

    def __init__(self, cookies: dict | None = None):
        self._cookies = cookies or {}

    def _request(self, method: str, url: str, retry_auth: bool = True, **kwargs) -> object:
        kwargs.setdefault("cookies", self._cookies)
        full_url = f"{self.BASE_URL}{url}" if url.startswith("/") else url
        try:
            resp = curl_requests.request(method, full_url, impersonate="chrome", **kwargs)
        except Exception as e:
            if "connect" in str(e).lower() or "timeout" in str(e).lower():
                raise NetworkError(f"Connection failed: {e}")
            raise
        if resp.status_code in (401, 403) and retry_auth:
            self._refresh_auth()
            return self._request(method, url, retry_auth=False, **kwargs)
        raise_for_status(resp)
        return resp

    def _refresh_auth(self):
        raise AuthError("Auth expired. Run: cli-web-{app_name} auth login", recoverable=False)

    # --- Endpoint methods (implement from <APP>.md) ---
```

**If protocol = html-scraping:** Same as REST but add `from bs4 import BeautifulSoup` and a `_parse_html(self, resp)` helper method.

**If protocol = GraphQL:** Same as REST but add a `_graphql(self, query, variables=None)` helper that POSTs to the GraphQL endpoint.

**If protocol = batchexecute:** Skeleton client that delegates to `core/rpc/` encoder/decoder. Include `_extract_tokens()` method for CSRF/session extraction.

### 3.6: `utils/helpers.py`

Generate with conditional sections based on `has_polling`, `has_context`, `has_partial_ids`:

```python
"""Shared CLI helpers for cli-web-{app_name}."""
import json
import sys
from contextlib import contextmanager
from pathlib import Path

import click

from cli_web.{app_name}.core.exceptions import {AppName}Error, _error_code_for

# --- Windows UTF-8 fix (stdout + stderr) ---
for stream_name in ("stdout", "stderr"):
    stream = getattr(sys, stream_name, None)
    if stream and hasattr(stream, "encoding"):
        if stream.encoding and stream.encoding.lower() not in ("utf-8", "utf8"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except AttributeError:
                pass


@contextmanager
def handle_errors(json_mode=False):
    """Catch exceptions, output structured errors, set exit codes."""
    try:
        yield
    except KeyboardInterrupt:
        sys.exit(130)
    except click.exceptions.Exit:
        raise
    except click.UsageError:
        raise
    except Exception as exc:
        code = _error_code_for(exc) if isinstance(exc, {AppName}Error) else "INTERNAL_ERROR"
        exit_code = 1 if code != "INTERNAL_ERROR" else 2
        if json_mode:
            error_dict = exc.to_dict() if hasattr(exc, "to_dict") else {
                "error": True, "code": code, "message": str(exc)
            }
            click.echo(json.dumps(error_dict))
        else:
            click.echo(f"Error: {exc}", err=True)
        sys.exit(exit_code)


def print_json(data):
    """Print JSON with indent for readability."""
    click.echo(json.dumps(data, indent=2, ensure_ascii=False))
```

**If has_partial_ids = true, append:**
```python
def resolve_partial_id(partial, items, id_attr="id", label_attr="title", kind="item"):
    """Resolve a partial ID prefix to a full item."""
    if len(partial) >= 20:
        for item in items:
            if getattr(item, id_attr, None) == partial:
                return item
        raise click.BadParameter(f"{kind} '{partial}' not found")
    partial_lower = partial.lower()
    matches = [i for i in items if getattr(i, id_attr, "").lower().startswith(partial_lower)]
    if len(matches) == 1:
        return matches[0]
    if len(matches) == 0:
        raise click.BadParameter(f"No {kind} matching '{partial}'")
    lines = [f"  {getattr(m, id_attr)[:16]}...  {getattr(m, label_attr, '')}" for m in matches[:5]]
    raise click.BadParameter(f"Ambiguous: '{partial}' matches {len(matches)} {kind}s:\n" + "\n".join(lines))
```

**If has_polling = true, append:**
```python
import time

def poll_until_complete(check_fn, timeout=300.0, initial_delay=2.0, max_delay=10.0, factor=1.5):
    """Poll with exponential backoff until check_fn returns a truthy value."""
    start = time.monotonic()
    delay = initial_delay
    while time.monotonic() - start < timeout:
        result = check_fn()
        if result:
            return result
        time.sleep(min(delay, max_delay))
        delay *= factor
    raise TimeoutError(f"Operation did not complete within {timeout}s")
```

**If has_context = true, append:**
```python
from cli_web.{app_name}.core.config import CONTEXT_FILE

def get_context_value(key):
    """Get a value from persistent context.json."""
    try:
        if CONTEXT_FILE.exists():
            return json.loads(CONTEXT_FILE.read_text(encoding="utf-8")).get(key)
    except (json.JSONDecodeError, OSError):
        pass
    return None

def set_context_value(key, value):
    """Set a value in persistent context.json."""
    ctx = {}
    try:
        if CONTEXT_FILE.exists():
            ctx = json.loads(CONTEXT_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        pass
    ctx[key] = value
    CONTEXT_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONTEXT_FILE.write_text(json.dumps(ctx, indent=2), encoding="utf-8")
```

### 3.7: `utils/output.py`

```python
"""Output formatting for cli-web-{app_name}."""
import json
import click


def json_success(data):
    """Print success JSON response."""
    click.echo(json.dumps({"success": True, "data": data}, indent=2, ensure_ascii=False))


def json_error(code, message, **extra):
    """Print error JSON response."""
    d = {"error": True, "code": code, "message": message}
    d.update(extra)
    click.echo(json.dumps(d))
```

### 3.8: `core/rpc/` (batchexecute only)

**`core/rpc/__init__.py`**: Empty.

**`core/rpc/types.py`**:
```python
"""RPC method IDs and URL constants for cli-web-{app_name}."""
from enum import Enum

# TODO: Populate from traffic-analysis.json RPC method IDs
class RPCMethod(Enum):
    pass  # e.g., LIST_ITEMS = "methodId123"

BATCHEXECUTE_URL = "https://FIXME.example.com/_/BatchExecute"  # TODO: Set from traffic
```

**`core/rpc/encoder.py`**:
```python
"""Encode batchexecute request bodies for cli-web-{app_name}.

See cli-anything-web-plugin/skills/methodology/references/google-batchexecute.md
for the wire format specification.
"""

def encode_rpc(method_id: str, params: list) -> dict:
    """Encode a single RPC call into batchexecute f.req format.

    TODO: Adapt param structure from captured traffic for each method.
    """
    import json
    inner = json.dumps([params])
    outer = json.dumps([[["" + method_id, inner, None, "generic"]]])
    return {"f.req": outer}
```

**`core/rpc/decoder.py`**:

NOTE: The triple-quoted docstrings below use standard Python `"""` syntax.
When writing this file, use normal triple quotes, not escaped ones.

```python
"""Decode batchexecute response bodies for cli-web-{app_name}.

Handles the )]}' prefix and length-prefixed chunks.
"""
import json

def decode_response(raw: str) -> list:
    """Decode a batchexecute response into parsed chunks."""
    # Strip )]}' prefix
    if raw.startswith(")]}'"):
        raw = raw[4:].lstrip("\n")

    results = []
    # TODO: Implement chunk parsing from traffic capture
    # See notebooklm reference for complete implementation
    return results
```

---

## Step 4: Post-Generation Checklist

After generating all files, verify:
- [ ] `cli_web/` directory has NO `__init__.py` (namespace package rule)
- [ ] `cli_web/{app_name}/` directory HAS `__init__.py`
- [ ] `core/__init__.py` exists (empty)
- [ ] `utils/__init__.py` exists (empty)
- [ ] All `{app_name}`, `{APP_NAME}`, `{AppName}` placeholders are replaced
- [ ] `client.py` has TODO comments for endpoint methods
- [ ] If batchexecute: `core/rpc/` directory exists with all 4 files
- [ ] If no-auth: config.py still exists (for config dir) but no auth.py generated
```

- [ ] **Step 3: Insert Step B.0 in the methodology skill**

In `cli-anything-web-plugin/skills/methodology/SKILL.md`, insert after line 167 (after "Package Structure" section, before "### Implementation Rules"):

```markdown

### Step B.0: Scaffold Core Modules

Before writing implementation code, read `${CLAUDE_PLUGIN_ROOT}/skills/boilerplate/SKILL.md`
and follow its instructions to scaffold the core/ modules. This generates exceptions.py,
client.py skeleton, helpers.py, config.py, and (for batchexecute) the rpc/ subpackage.

After scaffolding, review the generated files and customize `client.py` with actual
endpoint methods from `<APP>.md`.

```

- [ ] **Step 4: Verify the methodology edit**

```bash
sed -n '165,180p' cli-anything-web-plugin/skills/methodology/SKILL.md
```
Expected: "Package Structure" section, then "Step B.0: Scaffold Core Modules", then "Implementation Rules"

- [ ] **Step 5: Commit boilerplate skill + methodology update**

```bash
git add cli-anything-web-plugin/skills/boilerplate/ cli-anything-web-plugin/skills/methodology/SKILL.md
git commit -m "feat(plugin): add boilerplate generator skill for core/ scaffolding

New Claude-only skill generates exceptions.py, client.py, helpers.py,
config.py, output.py (and rpc/ for batchexecute) from protocol type and
auth configuration. Methodology skill Step B.0 references it.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 6: Cross-CLI Consistency Checker Agent

**Files:**
- Create: `cli-anything-web-plugin/agents/cross-cli-consistency-checker.md`

- [ ] **Step 1: Write the consistency checker agent**

Create `cli-anything-web-plugin/agents/cross-cli-consistency-checker.md`:

```markdown
---
name: cross-cli-consistency-checker
version: 0.1.0
description: >
  Audit all cli-web-* CLIs for convention drift against current HARNESS.md.
  Reports PASS/FAIL per check per CLI in a matrix format. Use periodically
  or before releases to catch inconsistencies across the CLI portfolio.
tools: [Read, Grep, Glob, Bash]
---

# Cross-CLI Consistency Checker

Audit all generated cli-web-* CLIs against current HARNESS.md conventions.
This is a read-only audit — it reports findings but does not auto-fix.

---

## Step 1: Discover CLIs

Read `registry.json` at the repository root to get the list of all CLIs.
For each entry, note the `directory`, `namespace`, and `auth` fields.

**Fallback:** If `registry.json` doesn't exist, glob for
`*/agent-harness/cli_web/*/__init__.py` to find CLI packages.

## Step 2: Locate Plugin Reference Files

Find the plugin's canonical `repl_skin.py` for version comparison using Glob:
```
Glob pattern: **/cli-anything-web-plugin/scripts/repl_skin.py
```

## Step 3: Run Check Matrix

For each discovered CLI, run all applicable checks. Mark checks as N/A
when they don't apply (e.g., auth checks for no-auth CLIs).

### Check 1: Exception Hierarchy (Critical)

Read `core/exceptions.py` and verify:
- Base error class exists with `to_dict()` method
- All 5 subtypes present: AuthError, RateLimitError, NetworkError, ServerError, NotFoundError
- `RateLimitError` has `retry_after` field AND `to_dict()` includes it
- `ServerError` stores `status_code` as instance attribute
- `raise_for_status()` maps: 401/403→AuthError, 404→NotFoundError, 429→RateLimitError, 5xx→ServerError

**How to check:**
```
Grep for "def to_dict" in exceptions.py
Grep for "retry_after" in exceptions.py — must appear in both __init__ and to_dict
Grep for "status_code" in ServerError class
```

### Check 2: UTF-8 Fix (Critical)

Read `*_cli.py` and verify BOTH stdout AND stderr are reconfigured:
```
Grep for "stdout.reconfigure" and "stderr.reconfigure" in *_cli.py
Both must be present. Only stdout = FAIL.
```

### Check 3: REPL Parsing (Critical)

Read `*_cli.py` and verify `shlex.split` is used in the REPL loop:
```
Grep for "shlex.split" in *_cli.py — must be present
Grep for "line.split()" in *_cli.py — must NOT be present (or only in non-REPL context)
```

### Check 4: REPL Dispatch (Critical)

Read `*_cli.py` and verify REPL dispatch uses `standalone_mode=False`:
```
Grep for "standalone_mode=False" in *_cli.py
Grep for "**ctx.params" in *_cli.py — must NOT be present
```

### Check 5: Namespace Package (Critical)

Verify `cli_web/__init__.py` does NOT exist at the agent-harness level:
```
Check: {dir}/cli_web/__init__.py should NOT exist
Check: {dir}/cli_web/{app}/__init__.py SHOULD exist
```

### Check 6: handle_errors Usage (Important)

Read all `commands/*.py` files and verify they use `handle_errors()`:
```
Grep for "with handle_errors" in commands/*.py — should appear in every command function
Grep for "except.*Exception" in commands/*.py — should NOT appear (manual try/except)
```

### Check 7: No click.ClickException (Important)

```
Grep for "click.ClickException" in commands/*.py and *_cli.py
Any match = FAIL (bypasses handle_errors JSON output)
```

### Check 8: JSON Error Format (Important)

Read `core/exceptions.py` and verify `to_dict()` returns structured format:
```
Grep for '"error".*True' in exceptions.py
Grep for '"code"' in exceptions.py
```

### Check 9: Auth Env Var (Important, auth CLIs only)

```
Grep for "CLI_WEB_.*_AUTH_JSON" in config.py or auth.py
N/A for no-auth CLIs.
```

### Check 10: Auth chmod (Important, auth CLIs only)

```
Grep for "chmod" or "0o600" in auth.py
N/A for no-auth CLIs.
```

### Check 11: repl_skin.py Version (Minor)

Compare `utils/repl_skin.py` against the plugin's canonical version:
```bash
diff {cli_dir}/utils/repl_skin.py {plugin_dir}/scripts/repl_skin.py
```
Any differences = FAIL (stale copy).

### Check 12: setup.py Namespaces (Important)

```
Grep for 'find_namespace_packages' in setup.py
Grep for 'include=\["cli_web\.\*"\]' in setup.py
```

## Step 4: Output Report

Format as a matrix table:

```
Cross-CLI Consistency Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━
                  ExcH  UTF8  REPL  Disp  NS    HErr  NoClk JSON  Auth  Chmd  Skin  Setup
futbin            PASS  FAIL  PASS  PASS  PASS  PASS  PASS  PASS  N/A   N/A   FAIL  PASS
reddit            PASS  PASS  PASS  PASS  PASS  FAIL  FAIL  PASS  PASS  PASS  PASS  PASS
...

Legend: ExcH=Exception Hierarchy, UTF8=UTF-8 Fix, REPL=shlex.split, Disp=REPL Dispatch,
        NS=Namespace Package, HErr=handle_errors, NoClk=No click.ClickException,
        JSON=JSON Error Format, Auth=Auth Env Var, Chmd=Auth chmod, Skin=repl_skin version,
        Setup=setup.py namespaces

Summary: X Critical, Y Important, Z Minor findings across N CLIs

Critical Issues:
  [CLI]: [check name] — [description] ([file:line])
  ...

Important Issues:
  [CLI]: [check name] — [description] ([file:line])
  ...

Minor Issues:
  [CLI]: [check name] — [description] ([file:line])
  ...
```
```

- [ ] **Step 2: Verify the file**

```bash
head -5 cli-anything-web-plugin/agents/cross-cli-consistency-checker.md
```

- [ ] **Step 3: Commit**

```bash
git add cli-anything-web-plugin/agents/cross-cli-consistency-checker.md
git commit -m "feat(plugin): add cross-CLI consistency checker agent

Audits all 12 cli-web-* CLIs against HARNESS.md conventions.
12-check matrix covering exception hierarchy, UTF-8, REPL patterns,
namespace packages, handle_errors, JSON format, auth, and repl_skin.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 7: CLI Gap Analyzer Skill

**Files:**
- Create: `cli-anything-web-plugin/skills/gap-analyzer/SKILL.md`
- Modify: `cli-anything-web-plugin/commands/refine.md` (lines 26-29)

- [ ] **Step 1: Create the gap-analyzer skill directory**

```bash
mkdir -p cli-anything-web-plugin/skills/gap-analyzer
```

- [ ] **Step 2: Write the gap analyzer skill**

Create `cli-anything-web-plugin/skills/gap-analyzer/SKILL.md`:

```markdown
---
name: gap-analyzer
version: 0.1.0
description: >
  Compare implemented CLI commands against <APP>.md API map to find missing
  endpoints, incomplete CRUD, dead client methods, and priority gaps.
  TRIGGER when: "gap analysis", "what's missing", "coverage report",
  "what endpoints are not implemented", or as a sub-step of the refine workflow.
  DO NOT trigger for: "refine" alone (use the /cli-anything-web:refine command).
---

# CLI Gap Analyzer

Produce a structured gap report comparing a CLI's documented API surface
against its implemented commands. Used during `/refine` workflows and
standalone coverage analysis.

---

## Inputs

You need the path to an existing CLI's agent-harness directory:
- `{APP_PATH}/agent-harness/` — the CLI root
- `{app}` — the app name (e.g., `reddit`, `hackernews`)

## Step 1: Parse Implemented Surface

Read all source files to build the set of implemented functionality:

### 1a. Extract Click commands

Read all files in `{APP_PATH}/agent-harness/cli_web/{app}/commands/`:
- For each file, find `@click.command()` and `@<group>.command()` decorators
- Extract: command group name, subcommand name, arguments, options
- Build list: `[(group, subcommand, [args], [options])]`

### 1b. Extract client methods

Read `{APP_PATH}/agent-harness/cli_web/{app}/core/client.py`:
- Find all public methods (not starting with `_`)
- For each method, note: name, HTTP method used (GET/POST/etc), URL pattern
- Build list: `[(method_name, http_verb, url_pattern)]`

### 1c. Map commands to client methods

For each Click command, trace which client method it calls:
- Read the command function body
- Find `client.method_name()` calls
- Build mapping: `{command: client_method}`

## Step 2: Parse Documented Surface

Read `{APP_PATH}/agent-harness/{APP_UPPER}.md` (the API map):
- Find the endpoint inventory section
- Extract each documented endpoint: resource group, HTTP method, URL, params, description
- Build list: `[(resource, http_verb, url, params, description)]`

## Step 3: Diff

Compare implemented vs documented:

### Missing Commands
Endpoints in `<APP>.md` that have no corresponding Click command:
```
For each documented endpoint:
  Find matching client method (by URL pattern or method name)
  Find matching Click command (that calls this client method)
  If no command found → MISSING
```

### Undocumented Commands
Click commands that call client methods not documented in `<APP>.md`:
```
For each Click command:
  Find the client method it calls
  Find the endpoint in <APP>.md for this method
  If no endpoint found → UNDOCUMENTED (possible hallucination)
```

### Dead Client Methods
Client methods that no Click command calls:
```
For each public client method:
  Search all commands/*.py for calls to this method
  If no command calls it → DEAD
```

### Incomplete CRUD
For each resource group, check CRUD coverage:
```
For each resource in <APP>.md:
  Check which CRUD ops the API supports (list, get, create, update, delete)
  Check which are implemented as commands
  If any supported op is missing → INCOMPLETE
```

## Step 4: Priority Scoring (Optional)

If `{APP_PATH}/traffic-capture/raw-traffic.json` exists:
- Count how many times each endpoint URL appears in captured requests
- Assign priority: HIGH (5+ hits), MED (2-4 hits), LOW (1 hit)
- Note: traffic captures are incomplete — endpoints not exercised during
  capture may be ranked LOW even if they are important to users

If raw-traffic.json doesn't exist, skip priority scoring and list all
gaps alphabetically.

## Step 5: Output Report

Present the gap report in this format:

```
Gap Report: cli-web-{app}
━━━━━━━━━━━━━━━━━━━━━━━━━
Coverage: X/Y endpoints (Z%)

Missing (HIGH priority):
  {HTTP_METHOD} {url} — {description} ({N} hits in traffic)
  ...

Missing (MED priority):
  {HTTP_METHOD} {url} — {description} ({N} hits)
  ...

Missing (LOW priority):
  {HTTP_METHOD} {url} — {description} ({N} hits)
  ...

Incomplete CRUD:
  {resource}: has {ops} ✓, missing {ops} ✗
  ...

Dead client methods:
  client.{method_name}() — not called by any command
  ...

Undocumented commands:
  {group} {subcommand} — calls client.{method}() but endpoint not in <APP>.md
  ...
```

If all endpoints are covered:
```
Gap Report: cli-web-{app}
━━━━━━━━━━━━━━━━━━━━━━━━━
Coverage: Y/Y endpoints (100%)
No gaps found. All documented endpoints are implemented.
```
```

- [ ] **Step 3: Update the refine command**

In `cli-anything-web-plugin/commands/refine.md`, replace step 3 (lines 26-29):

Old text:
```
3. **Gap analysis**:
   - Compare known endpoints vs implemented commands
   - If focus area specified, concentrate on that domain
   - If no focus, do broad gap analysis across all capabilities
```

New text:
```
3. **Gap analysis**: Read `${CLAUDE_PLUGIN_ROOT}/skills/gap-analyzer/SKILL.md` and
   follow its instructions to produce a structured gap report. If a focus area is
   specified, filter the report to that domain.
```

- [ ] **Step 4: Verify the refine edit**

```bash
sed -n '25,32p' cli-anything-web-plugin/commands/refine.md
```
Expected: step 3 references gap-analyzer skill

- [ ] **Step 5: Commit gap analyzer + refine update**

```bash
git add cli-anything-web-plugin/skills/gap-analyzer/ cli-anything-web-plugin/commands/refine.md
git commit -m "feat(plugin): add gap analyzer skill for structured refine workflow

New skill compares <APP>.md API map vs implemented commands to find
missing endpoints, incomplete CRUD, dead client methods, and
undocumented commands. Refine command step 3 now invokes it.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 8: Verify Plugin Structure

**Files:** None (verification only)

- [ ] **Step 1: Verify all new files exist**

```bash
ls -la cli-anything-web-plugin/agents/
ls -la cli-anything-web-plugin/skills/boilerplate/
ls -la cli-anything-web-plugin/skills/gap-analyzer/
```

Expected:
- `agents/`: 4 files (traffic-fidelity-reviewer, harness-compliance-reviewer, output-ux-reviewer, cross-cli-consistency-checker)
- `skills/boilerplate/`: SKILL.md
- `skills/gap-analyzer/`: SKILL.md

- [ ] **Step 2: Verify review-agents.md was deleted**

```bash
test -f cli-anything-web-plugin/skills/standards/references/review-agents.md && echo "FAIL: still exists" || echo "PASS: deleted"
```

- [ ] **Step 3: Verify no broken references**

```bash
grep -r "review-agents.md" cli-anything-web-plugin/
```
Expected: no matches (all references removed)

- [ ] **Step 4: Run plugin verification script**

```bash
bash cli-anything-web-plugin/verify-plugin.sh
```
Expected: all checks pass

- [ ] **Step 5: Final commit if any fixes needed**

Only if verify-plugin.sh revealed issues that needed fixing.
