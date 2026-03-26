# Review Agent Prompts

Three specialized agents for reviewing cli-web-* CLI implementations.
Each agent runs independently and returns scored findings.

## Important: Site Profile Awareness

Before scoring, determine the site profile:
- **No-auth sites**: Skip all auth-related checks (auth.py, auth commands,
  cookie priority, auth retry). Do NOT report missing auth features as findings.
- **Read-only sites**: Skip write operation checks.
- **No-RPC sites**: Skip batchexecute/RPC-specific checks.

Mark skipped checks as N/A, not as findings.

## Deduplication

Each agent has a specific scope. Do NOT report findings outside your scope:
- Traffic Fidelity: API map vs code only
- HARNESS Compliance: code quality and conventions only
- Output & UX: user-facing behavior only

---

## Agent 1: Traffic Fidelity

You are reviewing a generated CLI to verify it faithfully implements the
API surface discovered during traffic capture.

### Your Task

1. Read `{APP_PATH}/agent-harness/{APP_UPPER}.md` — this is the API map
   documenting every endpoint, its params, and expected response shape.
2. Read `{APP_PATH}/agent-harness/cli_web/{app}/core/client.py` — the HTTP
   client that implements each endpoint.
3. Read all files in `{APP_PATH}/agent-harness/cli_web/{app}/commands/` —
   the Click commands that expose client methods to users.
4. Compare what the API map documents vs what the code implements.

### What to Check

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

### Output Format

Return a list of findings, each with:
- **confidence**: 0-100 score
- **severity**: Critical / Important / Minor
- **file**: path:line
- **description**: What's wrong
- **evidence**: The specific mismatch (API map says X, code does Y)

---

## Agent 2: HARNESS Compliance

You are reviewing a generated CLI to verify it follows all HARNESS.md
conventions and the quality checklist — not just structurally, but in
actual code logic.

### Your Task

1. Read `cli-anything-web-plugin/HARNESS.md` — the methodology SOP.
2. Read `cli-anything-web-plugin/skills/standards/references/quality-checklist.md`
   — the 75-check quality checklist.
3. Read all source files in `{APP_PATH}/agent-harness/cli_web/{app}/`.
4. Check each applicable convention against the actual implementation.

### What to Check

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

### Output Format

Same as Agent 1: confidence, severity, file:line, description, evidence.

---

## Agent 3: Output & UX

You are reviewing a generated CLI from the end-user perspective — does
it work correctly, is help complete, is output clean?

### Your Task

1. Run `cli-web-{app} --help` and capture output.
2. Run each subcommand group's `--help` (e.g., `feed --help`, `search --help`).
3. Read `_print_repl_help()` in `{app}_cli.py` and compare against actual commands.
4. If auth is available, run a few commands with `--json` and inspect output.
5. Read `setup.py` and verify entry point matches CLI name.

### What to Check

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

### Output Format

Same as Agent 1: confidence, severity, file:line, description, evidence.
For output-related findings, include the actual output snippet as evidence.
