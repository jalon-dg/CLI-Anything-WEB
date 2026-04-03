---
name: boilerplate
version: 0.1.0
description: Generate core/ module scaffolds for cli-web-* CLIs. Produces exceptions.py, client.py, helpers.py, config.py, output.py, and (for batchexecute) the rpc/ subpackage. All files use placeholder syntax that the methodology skill fills in.
user-invocable: false
---

# Boilerplate Generator

This skill generates the core/ and utils/ module scaffolds that are 80% identical
across all cli-web-* CLIs. The methodology skill invokes this before writing
implementation-specific code.

---

## Step 1: Collect Inputs

Gather these parameters before generating any files. Each has a default or must
be supplied by the calling skill.

| Parameter | Type | Source | Example |
|-----------|------|--------|---------|
| `app_name` | str | From CLI name (`cli-web-<app>` -> `<app>`) | `hackernews` |
| `APP_NAME` | str | UPPER_SNAKE of app_name (replace hyphens with underscores before uppercasing, e.g., `gh-trending` -> `GH_TRENDING`) | `HACKERNEWS` |
| `AppName` | str | PascalCase of app_name | `HackerNews` |
| `protocol` | enum | Traffic analysis: `rest`, `graphql`, `html-scraping`, `batchexecute` | `rest` |
| `http_client` | enum | Traffic analysis: `httpx`, `curl_cffi` | `httpx` |
| `auth_type` | enum | Site profile: `none`, `cookie`, `api-key`, `token`, `google-sso` | `cookie` |
| `resources` | list[str] | From `<APP>.md` endpoint groups | `["stories", "users", "search"]` |
| `has_polling` | bool | Any async/long-running operations? | `false` |
| `has_context` | bool | Does the CLI need `use <id>` / `status` context? | `false` |
| `has_partial_ids` | bool | Do resource IDs support prefix matching? | `false` |

---

## Step 2: Decision Matrix

Which parameters affect which files:

| File | Always | Conditional on |
|------|--------|----------------|
| `__init__.py` | Yes | -- |
| `__main__.py` | Yes | -- |
| `core/exceptions.py` | Yes | -- |
| `core/config.py` | Yes | `auth_type` (skip AUTH_FILE/AUTH_ENV_VAR if `none`) |
| `core/client.py` | Yes | `protocol`, `http_client` |
| `core/auth.py` | No | `auth_type != none` |
| `utils/helpers.py` | Yes | `has_polling`, `has_context`, `has_partial_ids` |
| `utils/output.py` | Yes | -- |
| `core/rpc/__init__.py` | No | `protocol == batchexecute` |
| `core/rpc/types.py` | No | `protocol == batchexecute` |
| `core/rpc/encoder.py` | No | `protocol == batchexecute` |
| `core/rpc/decoder.py` | No | `protocol == batchexecute` |

### File Generation Table

Generate each file by copying the template below, replacing all `{app_name}`,
`{APP_NAME}`, and `{AppName}` placeholders with the actual values. Include or
exclude conditional sections as indicated by the decision matrix.

---

## Step 3: Generate Files

### 3.1: `cli_web/{app_name}/__init__.py`

```python
"""cli-web-{app_name}: CLI for {AppName}."""

__version__ = "0.1.0"
```

### 3.2: `cli_web/{app_name}/__main__.py`

```python
"""Allow running as: python -m cli_web.{app_name}"""
from .{app_name}_cli import cli

if __name__ == "__main__":
    cli()
```

### 3.3: `core/exceptions.py`

```python
"""Typed exception hierarchy for cli-web-{app_name}.

Every exception carries enough context for:
- Retry decisions (recoverable flag, retry_after)
- Structured JSON output (to_dict / error_code_for)
- CLI exit codes (auth=1, server=2, network=3)
"""
from __future__ import annotations


class {AppName}Error(Exception):
    """Base exception for all cli-web-{app_name} errors."""

    def to_dict(self) -> dict:
        return {{
            "error": True,
            "code": _error_code_for(self),
            "message": str(self),
        }}


class AuthError({AppName}Error):
    """Authentication failed -- expired cookies, invalid tokens, session timeout.

    Args:
        recoverable: If True, client retries once (token refresh).
                     If False, user must re-login.
    """

    def __init__(self, message: str, recoverable: bool = True):
        self.recoverable = recoverable
        super().__init__(message)


class RateLimitError({AppName}Error):
    """Server returned 429 -- too many requests.

    Args:
        retry_after: Seconds to wait before retrying (from Retry-After header).
    """

    def __init__(self, message: str, retry_after: float | None = None):
        self.retry_after = retry_after
        super().__init__(message)

    def to_dict(self) -> dict:
        d = super().to_dict()
        if self.retry_after is not None:
            d["retry_after"] = self.retry_after
        return d


class NetworkError({AppName}Error):
    """Connection failed -- DNS resolution, TCP connect, TLS handshake."""


class ServerError({AppName}Error):
    """Server returned 5xx -- internal error, bad gateway, service unavailable.

    Args:
        status_code: The HTTP status code (500, 502, 503, etc.)
    """

    def __init__(self, message: str, status_code: int = 500):
        self.status_code = status_code
        super().__init__(message)


class NotFoundError({AppName}Error):
    """Resource not found (HTTP 404)."""


class RPCError({AppName}Error):
    """RPC call failed (batchexecute decode error, unexpected response shape)."""


# --- HTTP status code mapping ---

_CODE_MAP = {{
    401: lambda msg: AuthError(msg, recoverable=True),
    403: lambda msg: AuthError(msg, recoverable=True),
    404: lambda msg: NotFoundError(msg),
    # 429 handled separately below to extract Retry-After header
}}


def _error_code_for(exc: {AppName}Error) -> str:
    """Map exception type to a JSON error code string."""
    mapping = {{
        AuthError: "AUTH_EXPIRED",
        RateLimitError: "RATE_LIMITED",
        NotFoundError: "NOT_FOUND",
        ServerError: "SERVER_ERROR",
        NetworkError: "NETWORK_ERROR",
        RPCError: "RPC_ERROR",
    }}
    for exc_type, code in mapping.items():
        if isinstance(exc, exc_type):
            return code
    return "UNKNOWN_ERROR"


def raise_for_status(response) -> None:
    """Map HTTP response status to a typed exception. Call after every request."""
    if response.status_code < 400:
        return

    text = getattr(response, "text", "")[:200]
    msg = f"HTTP {{response.status_code}}: {{text}}"

    # Specific status codes
    if response.status_code in _CODE_MAP:
        raise _CODE_MAP[response.status_code](msg)

    # Extract Retry-After for 429
    if response.status_code == 429:
        retry_after = None
        if hasattr(response, "headers"):
            raw = response.headers.get("Retry-After")
            if raw:
                retry_after = float(raw)
        raise RateLimitError(msg, retry_after=retry_after)

    # 5xx range
    if 500 <= response.status_code < 600:
        raise ServerError(msg, status_code=response.status_code)

    # 4xx fallback
    raise {AppName}Error(msg)
```

### 3.4: `core/config.py`

```python
"""Configuration constants for cli-web-{app_name}."""
from pathlib import Path

APP_NAME = "cli-web-{app_name}"
CONFIG_DIR = Path.home() / ".config" / APP_NAME
# --- conditional: auth_type != "none" ---
AUTH_FILE = "auth.json"
AUTH_ENV_VAR = "CLI_WEB_{APP_NAME}_AUTH_JSON"
# --- end conditional ---
# --- conditional: has_context ---
CONTEXT_FILE = "context.json"
# --- end conditional ---


def get_config_dir() -> Path:
    """Return (and create) the config directory."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    return CONFIG_DIR


# --- conditional: auth_type != "none" ---
def get_auth_path() -> Path:
    """Return the path to auth.json, creating config dir if needed."""
    return get_config_dir() / AUTH_FILE
# --- end conditional ---
```

**If `auth_type == "none"`**: Remove the lines between `--- conditional: auth_type != "none" ---`
markers (AUTH_FILE, AUTH_ENV_VAR, and get_auth_path).

**If `has_context == false`**: Remove the CONTEXT_FILE line.

### 3.4b: `core/auth.py` (Cookie 模式)

当 `auth_type = "cookie"` 时使用此模板：

```python
"""Authentication management for cli-web-{app_name} (Cookie mode)."""
from __future__ import annotations

import json
from pathlib import Path

from .config import AUTH_DIR, get_auth_path
from .exceptions import AuthError

AUTH_JSON_FILE = AUTH_DIR / "auth.json"


def load_cookies() -> dict:
    """从文件或环境变量加载认证 cookie.

    Returns:
        Cookie 字典

    Raises:
        AuthError if no auth found
    """
    import os

    # 优先从环境变量加载
    env_auth = os.environ.get(f"CLI_WEB_{APP_NAME}_AUTH_JSON")
    if env_auth:
        try:
            return json.loads(env_auth)
        except json.JSONDecodeError:
            pass

    # 从 auth.json 文件加载
    if AUTH_JSON_FILE.exists():
        return json.loads(AUTH_JSON_FILE.read_text(encoding="utf-8"))

    raise AuthError(
        f"No auth found. Run: cli-web-{app_name} auth login"
    )


def save_cookies(cookies: dict) -> None:
    """保存认证 cookie 到文件.

    Args:
        cookies: 要保存的 cookie 字典
    """
    AUTH_DIR.mkdir(parents=True, exist_ok=True)
    AUTH_JSON_FILE.write_text(
        json.dumps(cookies, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    try:
        AUTH_JSON_FILE.chmod(0o600)
    except Exception:
        pass  # Windows 可能不支持


def clear_auth() -> None:
    """清除保存的认证信息."""
    if AUTH_JSON_FILE.exists():
        AUTH_JSON_FILE.unlink()


def get_auth_status() -> dict:
    """获取当前认证状态.

    Returns:
        Dict with "status" key: "valid" or "missing"
    """
    try:
        cookies = load_cookies()
        if cookies:
            return {"status": "valid", "cookies": list(cookies.keys())}
    except AuthError:
        pass
    return {"status": "missing"}
```

### 3.4c: `core/auth.py` (Token 模式)

当 `auth_type = "token"` 时使用此模板：

```python
"""Authentication management for cli-web-{app_name} (Token mode)."""
from __future__ import annotations

import os
from pathlib import Path

from .config import AUTH_DIR, get_auth_path
from .exceptions import AuthError

TOKEN_FILE = AUTH_DIR / "token"
TOKEN_HEADER = "Access-Token"  # 可根据实际调整


def load_token() -> str:
    """从文件或环境变量加载 token.

    Returns:
        Token 字符串

    Raises:
        AuthError if no token found
    """
    # 优先从环境变量加载
    env_token = os.environ.get(f"CLI_WEB_{APP_NAME}_TOKEN")
    if env_token:
        return env_token

    # 从 token 文件加载
    if TOKEN_FILE.exists():
        return TOKEN_FILE.read_text(encoding="utf-8").strip()

    raise AuthError(
        f"No token found. Run: cli-web-{app_name} auth login"
    )


def save_token(token: str) -> None:
    """保存 token 到文件.

    Args:
        token: 要保存的 token 字符串
    """
    AUTH_DIR.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(token, encoding="utf-8")
    try:
        TOKEN_FILE.chmod(0o600)
    except Exception:
        pass  # Windows 可能不支持


def clear_auth() -> None:
    """清除保存的认证信息."""
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()


def get_auth_status() -> dict:
    """获取当前认证状态.

    Returns:
        Dict with "status" key: "valid" or "missing"
    """
    try:
        token = load_token()
        if token:
            return {"status": "valid", "token": token[:10] + "..."}
    except AuthError:
        pass
    return {"status": "missing"}


# Token 模式的 login 函数（需要用 playwright 提取 localStorage）
def login_browser(username: str, password: str, storage_key: str = "haier-user-center-access-token"):
    """用 Playwright 登录，提取 localStorage 中的 token.

    Args:
        username: 用户名
        password: 密码
        storage_key: localStorage 中的 token key
    """
    import asyncio
    from playwright.sync_api import sync_playwright

    print(f"Opening browser for login to extract token from localStorage['{storage_key}']...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 导航到登录页（需要根据实际登录 URL 调整）
        page.goto("https://e.haier.net/login")

        # 填入用户名密码并登录
        page.fill('input[name="username"]', username)
        page.fill('input[name="password"]', password)
        page.click('button[type="submit"]')

        # 等待登录完成
        page.wait_for_load_state("networkidle")

        # 提取 localStorage 中的 token
        token = page.evaluate(f"localStorage.getItem('{storage_key}')")

        browser.close()

        if not token:
            raise AuthError(f"Failed to extract token from localStorage['{storage_key}']")

        save_token(token)
        print(f"Login successful! Token saved.")
```

### 3.5: `core/client.py`

Generate ONE of the following variants based on `protocol` and `http_client`.

#### Variant A: REST + httpx

```python
"""HTTP client for cli-web-{app_name}."""
from __future__ import annotations

import httpx

from .exceptions import (
    {AppName}Error,
    AuthError,
    NetworkError,
    raise_for_status,
)


class {AppName}Client:
    """REST client with auth retry and typed exceptions."""

    BASE_URL = "https://FILL_IN_BASE_URL"

    def __init__(self, cookies: dict | None = None, api_key: str | None = None, token: str | None = None):
        self._cookies = cookies or {{}}
        self._api_key = api_key
        self._token = token
        headers = {{"User-Agent": "cli-web-{app_name}/0.1.0"}}
        # 根据 auth_type 使用不同的认证方式
        if self._token:
            # token 模式：使用自定义的 Token Header
            headers["Access-Token"] = self._token
        elif self._api_key:
            # api-key 模式：使用 Bearer Token
            headers["Authorization"] = f"Bearer {{self._api_key}}"
        self._client = httpx.Client(
            base_url=self.BASE_URL,
            timeout=httpx.Timeout(connect=10.0, read=30.0, write=30.0, pool=30.0),
            headers=headers,
        )

    def _request(
        self,
        method: str,
        path: str,
        *,
        retry_on_auth: bool = True,
        **kwargs,
    ) -> httpx.Response:
        kwargs.setdefault("cookies", self._cookies)
        try:
            resp = self._client.request(method, path, **kwargs)
        except httpx.ConnectError as exc:
            raise NetworkError(f"Connection failed: {{exc}}")
        except httpx.TimeoutException as exc:
            raise NetworkError(f"Request timed out: {{exc}}")

        if resp.status_code in (401, 403) and retry_on_auth:
            self._refresh_auth()
            return self._request(method, path, retry_on_auth=False, **kwargs)

        raise_for_status(resp)
        return resp

    def _refresh_auth(self) -> None:
        """Override to implement token refresh logic."""
        raise AuthError("Auth expired. Run: cli-web-{app_name} auth login", recoverable=False)

    # --- Add endpoint methods here ---
    # def list_items(self) -> list[dict]:
    #     resp = self._request("GET", "/api/items")
    #     return resp.json()

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
```

#### Variant B: REST + curl_cffi

```python
"""HTTP client for cli-web-{app_name} (curl_cffi for anti-bot bypass)."""
from __future__ import annotations

from curl_cffi import requests as curl_requests

from .exceptions import (
    {AppName}Error,
    AuthError,
    NetworkError,
    raise_for_status,
)


class {AppName}Client:
    """REST client using curl_cffi Chrome TLS impersonation."""

    BASE_URL = "https://FILL_IN_BASE_URL"

    def __init__(self, cookies: dict | None = None, api_key: str | None = None, token: str | None = None):
        self._cookies = cookies or {{}}
        self._api_key = api_key
        self._token = token
        self._session = curl_requests.Session(impersonate="chrome")
        headers = {{"User-Agent": "cli-web-{app_name}/0.1.0"}}
        # 根据 auth_type 使用不同的认证方式
        if self._token:
            # token 模式：使用自定义的 Token Header
            headers["Access-Token"] = self._token
        elif self._api_key:
            # api-key 模式：使用 Bearer Token
            headers["Authorization"] = f"Bearer {{self._api_key}}"
        self._session.headers.update(headers)

    def _request(
        self,
        method: str,
        url: str,
        *,
        retry_on_auth: bool = True,
        **kwargs,
    ):
        if not url.startswith("http"):
            url = self.BASE_URL + url
        kwargs.setdefault("cookies", self._cookies)
        try:
            resp = self._session.request(method, url, **kwargs)
        except Exception as exc:
            raise NetworkError(f"Connection failed: {{exc}}")

        if resp.status_code in (401, 403) and retry_on_auth:
            self._refresh_auth()
            return self._request(method, url, retry_on_auth=False, **kwargs)

        raise_for_status(resp)
        return resp

    def _refresh_auth(self) -> None:
        raise AuthError("Auth expired. Run: cli-web-{app_name} auth login", recoverable=False)

    # --- Add endpoint methods here ---

    def close(self):
        self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
```

#### Variant C: HTML Scraping (httpx or curl_cffi)

Use Variant A or B as the base, then add this import and method:

```python
from bs4 import BeautifulSoup

# Add to class body:
def _parse_html(self, html: str) -> BeautifulSoup:
    """Parse HTML response into a BeautifulSoup tree."""
    return BeautifulSoup(html, "html.parser")
```

#### Variant D: GraphQL (httpx or curl_cffi)

Use Variant A or B as the base, then add this method:

```python
# Add to class body:
def _graphql(self, query: str, variables: dict | None = None) -> dict:
    """Execute a GraphQL query and return the data payload."""
    payload = {{"query": query}}
    if variables:
        payload["variables"] = variables
    resp = self._request("POST", "/graphql", json=payload)
    body = resp.json()
    if "errors" in body:
        raise {AppName}Error(f"GraphQL error: {{body['errors'][0].get('message', body['errors'])}}")
    return body.get("data", {{}})
```

#### Variant E: batchexecute

```python
"""HTTP client for cli-web-{app_name} (Google batchexecute RPC)."""
from __future__ import annotations

import httpx

from .exceptions import (
    {AppName}Error,
    AuthError,
    NetworkError,
    RPCError,
    raise_for_status,
)
from .rpc.encoder import encode_rpc
from .rpc.decoder import decode_response
from .rpc.types import RPCMethod


class {AppName}Client:
    """Google batchexecute RPC client."""

    BASE_URL = "https://FILL_IN_BASE_URL"
    BATCHEXECUTE_PATH = "/_/FILL_IN_SERVICE/data/batchexecute"

    def __init__(self, cookies: dict | None = None):
        self._cookies = cookies or {{}}
        self._csrf_token: str | None = None
        self._session_id: str | None = None
        self._client = httpx.Client(
            base_url=self.BASE_URL,
            timeout=httpx.Timeout(connect=10.0, read=60.0, write=30.0, pool=30.0),
            headers={{"User-Agent": "cli-web-{app_name}/0.1.0"}},
        )

    def _rpc(self, method: RPCMethod, params: list) -> list:
        """Execute an RPC call and return the decoded response."""
        body = encode_rpc(method, params, csrf_token=self._csrf_token)
        try:
            resp = self._client.post(
                self.BATCHEXECUTE_PATH,
                data=body,
                cookies=self._cookies,
            )
        except httpx.ConnectError as exc:
            raise NetworkError(f"Connection failed: {{exc}}")
        except httpx.TimeoutException as exc:
            raise NetworkError(f"Request timed out: {{exc}}")

        raise_for_status(resp)
        return decode_response(resp.text, method)

    def _refresh_tokens(self) -> None:
        """Fetch homepage to extract fresh CSRF/session tokens."""
        import re
        resp = self._client.get("/", cookies=self._cookies, follow_redirects=True)
        if resp.status_code != 200:
            raise AuthError("Token refresh failed. Run: cli-web-{app_name} auth login", recoverable=False)
        # Customize these regex patterns for the target app
        html = resp.text
        m = re.search(r'"SNlM0e"\s*:\s*"([^"]+)"', html)
        if m:
            self._csrf_token = m.group(1)

    # --- Add RPC method wrappers here ---

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
```

### 3.6: `utils/helpers.py`

```python
"""Shared helpers for cli-web-{app_name}."""
from __future__ import annotations

import io
import json
import sys
from contextlib import contextmanager

import click

from ..core.exceptions import {AppName}Error, _error_code_for


# --- Windows UTF-8 fix (always include) ---
def ensure_utf8() -> None:
    """Force UTF-8 on stdout and stderr for Windows compatibility."""
    if sys.platform == "win32":
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        else:
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, encoding="utf-8", errors="replace"
            )
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        else:
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer, encoding="utf-8", errors="replace"
            )


# --- Structured error handler ---
@contextmanager
def handle_errors(json_mode: bool = False):
    """Catch domain exceptions and emit structured output or Rich errors.

    Usage:
        with handle_errors(json_mode=ctx.obj.get("json")):
            do_something()
    """
    try:
        yield
    except KeyboardInterrupt:
        raise SystemExit(130)
    except (click.exceptions.Exit, click.UsageError):
        raise
    except {AppName}Error as exc:
        if json_mode:
            print_json(exc.to_dict())
        else:
            click.secho(f"Error: {{exc}}", fg="red", err=True)
        raise SystemExit(1)
    except Exception as exc:
        if json_mode:
            print_json({{"error": True, "code": "INTERNAL_ERROR", "message": str(exc)}})
        else:
            click.secho(f"Error: {{exc}}", fg="red", err=True)
        raise SystemExit(2)


def print_json(data) -> None:
    """Print data as formatted JSON to stdout."""
    print(json.dumps(data, indent=2, ensure_ascii=False, default=str))


# --- conditional: has_partial_ids ---
def resolve_partial_id(partial: str, items: list[dict], key: str = "id") -> dict:
    """Resolve a partial ID prefix to a single item.

    Raises {AppName}Error if zero or multiple matches.
    """
    matches = [item for item in items if str(item.get(key, "")).startswith(partial)]
    if len(matches) == 0:
        raise {AppName}Error(f"No item found matching '{{partial}}'")
    if len(matches) > 1:
        ids = [str(m.get(key, "")) for m in matches[:5]]
        raise {AppName}Error(f"Ambiguous ID '{{partial}}', matches: {{', '.join(ids)}}")
    return matches[0]
# --- end conditional: has_partial_ids ---


# --- conditional: has_polling ---
def poll_until_complete(
    check_fn,
    *,
    timeout: float = 300.0,
    initial_delay: float = 2.0,
    max_delay: float = 10.0,
    backoff_factor: float = 1.5,
):
    """Poll check_fn with exponential backoff until it returns a truthy value.

    Args:
        check_fn: Callable that returns a result (truthy = done) or None/falsy.
        timeout: Maximum total wait time in seconds.
        initial_delay: First sleep interval.
        max_delay: Cap on sleep interval.
        backoff_factor: Multiplier per iteration.

    Returns:
        The truthy result from check_fn.

    Raises:
        {AppName}Error if timeout is exceeded.
    """
    import time

    elapsed = 0.0
    delay = initial_delay
    while elapsed < timeout:
        result = check_fn()
        if result:
            return result
        time.sleep(delay)
        elapsed += delay
        delay = min(delay * backoff_factor, max_delay)
    raise {AppName}Error(f"Operation timed out after {{timeout}}s")
# --- end conditional: has_polling ---


# --- conditional: has_context ---
def get_context_value(key: str) -> str | None:
    """Read a value from the persistent context file."""
    from ..core.config import CONFIG_DIR, CONTEXT_FILE

    path = CONFIG_DIR / CONTEXT_FILE
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    return data.get(key)


def set_context_value(key: str, value: str) -> None:
    """Write a value to the persistent context file."""
    from ..core.config import CONFIG_DIR, CONTEXT_FILE

    path = CONFIG_DIR / CONTEXT_FILE
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    data = {{}}
    if path.exists():
        data = json.loads(path.read_text())
    data[key] = value
    path.write_text(json.dumps(data, indent=2))
# --- end conditional: has_context ---
```

**Conditional sections**: Remove the blocks between `--- conditional: ... ---` /
`--- end conditional: ... ---` markers when the corresponding flag is `false`.

### 3.7: `utils/output.py`

```python
"""Structured JSON output helpers for cli-web-{app_name}."""
from __future__ import annotations

import json


def json_success(data, **extra) -> str:
    """Format a successful result as JSON string."""
    payload = {{"success": True, "data": data}}
    payload.update(extra)
    return json.dumps(payload, indent=2, ensure_ascii=False, default=str)


def json_error(code: str, message: str, **extra) -> str:
    """Format an error result as JSON string."""
    payload = {{"error": True, "code": code, "message": message}}
    payload.update(extra)
    return json.dumps(payload, indent=2, ensure_ascii=False, default=str)
```

### 3.8: `core/rpc/` (batchexecute only)

Only generate these files when `protocol == "batchexecute"`.

#### `core/rpc/__init__.py`

```python
"""RPC encoding/decoding for Google batchexecute protocol."""
```

#### `core/rpc/types.py`

```python
"""RPC method definitions for cli-web-{app_name}.

Each method maps to a batchexecute RPC ID discovered from traffic capture.
IMPORTANT: Verify every RPC ID against captured traffic. The same endpoint
may use different param structures for different operations.
"""
from __future__ import annotations

from enum import Enum


class RPCMethod(Enum):
    """Known RPC methods.

    Format: NAME = ("rpc_id", "human_description")
    Fill in from <APP>.md after traffic analysis.
    """

    # EXAMPLE = ("AbCdEf", "Example operation description")
    pass
```

#### `core/rpc/encoder.py`

```python
"""Encode RPC requests for Google batchexecute.

Builds the f.req form body expected by /_/SERVICE/data/batchexecute.
"""
from __future__ import annotations

import json

from .types import RPCMethod


def encode_rpc(
    method: RPCMethod,
    params: list,
    *,
    csrf_token: str | None = None,
) -> dict:
    """Encode an RPC call into a batchexecute form body.

    Returns a dict suitable for httpx data= parameter.
    """
    rpc_id = method.value[0]
    inner = json.dumps(params, separators=(",", ":"))
    req_body = json.dumps([[
        [rpc_id, inner, None, "generic"],
    ]], separators=(",", ":"))
    body = {{"f.req": req_body}}
    if csrf_token:
        body["at"] = csrf_token
    return body
```

#### `core/rpc/decoder.py`

```python
"""Decode batchexecute RPC responses.

Google batchexecute responses have a prefix line (e.g., )]}'\\n) followed
by length-prefixed JSON arrays. This module strips the prefix and parses
the inner payload.
"""
from __future__ import annotations

import json

from ..exceptions import RPCError
from .types import RPCMethod


def decode_response(raw: str, method: RPCMethod) -> list:
    """Decode a batchexecute response and return the inner payload.

    Args:
        raw: The full response text from batchexecute endpoint.
        method: The RPC method that was called (for error context).

    Returns:
        Parsed inner JSON array from the RPC response.

    Raises:
        RPCError: If the response cannot be parsed.
    """
    # Strip the security prefix
    lines = raw.split("\\n")
    for i, line in enumerate(lines):
        if line.strip().startswith("[["):
            break
    else:
        raise RPCError(f"Cannot parse batchexecute response for {{method.value[0]}}")

    try:
        outer = json.loads(lines[i])
    except json.JSONDecodeError as exc:
        raise RPCError(f"JSON decode failed for {{method.value[0]}}: {{exc}}")

    # Navigate to inner payload: outer[0][2] contains the JSON string
    try:
        inner_str = outer[0][2]
        if isinstance(inner_str, str):
            return json.loads(inner_str)
        return inner_str
    except (IndexError, TypeError, json.JSONDecodeError) as exc:
        raise RPCError(f"Inner payload extraction failed for {{method.value[0]}}: {{exc}}")
```

---

## Step 4: Post-Generation Checklist

After generating all files, verify:

- [ ] `cli_web/` directory has NO `__init__.py` (namespace package)
- [ ] `cli_web/{app_name}/` directory HAS `__init__.py` (sub-package)
- [ ] All `{app_name}`, `{APP_NAME}`, `{AppName}` placeholders are replaced with actual values
- [ ] `FILL_IN_BASE_URL` is noted as requiring replacement during implementation
- [ ] `core/exceptions.py` has `to_dict()` on base class and override on `RateLimitError`
- [ ] `utils/helpers.py` Windows UTF-8 fix covers BOTH stdout AND stderr
- [ ] Conditional sections (polling, context, partial IDs) match the collected inputs
- [ ] For `batchexecute` protocol: `core/rpc/` directory exists with all four files
- [ ] For non-`batchexecute` protocol: `core/rpc/` directory does NOT exist
- [ ] `setup.py` uses `find_namespace_packages(include=["cli_web.*"])`
