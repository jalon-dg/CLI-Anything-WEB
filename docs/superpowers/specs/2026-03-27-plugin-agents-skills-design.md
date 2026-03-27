# Plugin Agents & Skills Design

**Date**: 2026-03-27
**Scope**: Add 4 components to `cli-anything-web-plugin/`: 3 review agents, 1 boilerplate skill, 1 consistency checker agent, 1 gap analyzer skill

---

## 1. Three Review Agents

### Location
```
cli-anything-web-plugin/agents/
├── traffic-fidelity-reviewer.md
├── harness-compliance-reviewer.md
└── output-ux-reviewer.md
```

### Design

Each agent is a proper Claude Code plugin agent file with frontmatter (`name`, `version: 0.1.0`, `description`, `tools`). The content is migrated from `skills/standards/references/review-agents.md` — each agent gets its own section from that file.

**Agent 1: traffic-fidelity-reviewer**
- Tools: Read, Grep, Glob
- Reads: `<APP>.md` (API map), `client.py`, `commands/`
- Checks: endpoint coverage, parameter fidelity, response parsing, dead client methods, stale API map
- Output: findings with confidence (0-100), severity (Critical/Important/Minor), file:line, evidence

**Agent 2: harness-compliance-reviewer**
- Tools: Read, Grep, Glob
- Reads: HARNESS.md, quality-checklist.md, all source files
- Checks: exception hierarchy (`to_dict()`, `retry_after`, `status_code`), auth patterns (chmod 600, env var, cookie priority), client architecture (auth retry, backoff, no bare except), CLI patterns (UTF-8 both streams, `shlex.split`, `handle_errors`), JSON output (`click.ClickException` bypass detection)
- Output: same format as Agent 1

**Agent 3: output-ux-reviewer**
- Tools: Read, Grep, Glob, Bash
- Reads: `--help` output, `_print_repl_help()`, `setup.py`
- Checks: help completeness (all groups listed, all subcommands listed), REPL help sync against actual commands, JSON output quality (no protocol leaks), entry point correctness, dead command files
- Output: same format as Agent 1

### Site Profile Awareness

All 3 agents include site profile logic at the top:
- No-auth sites: skip auth checks, mark N/A
- Read-only sites: skip write operation checks
- No-RPC sites: skip batchexecute/RPC checks

### Deduplication Scope

Each agent has strict scope boundaries to prevent duplicate findings:
- Traffic Fidelity: API map vs code only
- HARNESS Compliance: code quality and conventions only
- Output & UX: user-facing behavior only

### Plugin Manifest

Claude Code auto-discovers `agents/`, `commands/`, and `skills/` directories in plugins. No changes to `plugin.json` required — verified by existing auto-discovery of `commands/` and `skills/` which also have no manifest entries.

### Standards Skill Changes

In `skills/standards/SKILL.md` Step 1 (lines 49-75), replace the full block:

**Old text** (lines 53-56):
```
Dispatch 3 agents in the **same message** using the Agent tool. Read the
complete agent prompts from `references/review-agents.md`.
```

**New text**:
```
Dispatch 3 plugin agents in the **same message** using the Agent tool:
- `traffic-fidelity-reviewer` — API coverage (reads <APP>.md + client.py + commands/)
- `harness-compliance-reviewer` — Code conventions (reads HARNESS.md + all source)
- `output-ux-reviewer` — User experience (runs --help, checks REPL, validates JSON)

Pass each agent: APP_PATH=`{app}/agent-harness`, APP_NAME=`{app}`, and site
profile (auth_type, is_read_only). The agents are defined in the plugin's
`agents/` directory.
```

The rest of Step 1 (filtering, categorization, gate) remains unchanged.

### Deletion

Delete `skills/standards/references/review-agents.md` after migration. No duplication. Only referenced by standards SKILL.md (which is updated above) — verified safe.

---

## 2. Boilerplate Generator Skill

### Location
```
cli-anything-web-plugin/skills/boilerplate/
└── SKILL.md
```

### Design

A Claude-only skill that generates core/ module scaffolds based on protocol type, HTTP client, and auth type.

**Frontmatter**:
```yaml
name: boilerplate
version: 0.1.0
description: >
  Generate core/ module scaffolds (exceptions.py, client.py, helpers.py, config.py)
  from protocol type, auth type, and resource list. Reduces Phase 2 setup from
  hours to minutes.
user-invocable: false
```

### Invocation

The methodology SKILL.md Step B.0 instructs: "Read `${CLAUDE_PLUGIN_ROOT}/skills/boilerplate/SKILL.md` and follow its instructions to scaffold the core modules." This is consistent with how the methodology skill already references other plugin files (e.g., `references/traffic-patterns.md`).

### Inputs

Derived from `traffic-analysis.json` (primary) or `<APP>.md` (fallback if analyzer wasn't run):
- `app_name`: e.g., `hackernews`
- `protocol`: REST | GraphQL | batchexecute | html-scraping | ssr-nextdata | browser-rendered
- `http_client`: httpx | curl_cffi
- `auth_type`: none | cookie | google-sso | api-key
- `resources`: list of resource group names (e.g., stories, search, user)
- `has_polling`: boolean (for generation/async apps)
- `has_context`: boolean (for multi-resource apps with `use <id>`)
- `has_partial_ids`: boolean (for UUID-based apps)

### Generated Files

| File | Condition | Content |
|------|-----------|---------|
| `core/exceptions.py` | Always | Full hierarchy: AppError → AuthError, RateLimitError, NetworkError, ServerError, NotFoundError. Includes `to_dict()`, `retry_after`, `status_code`. App name in class prefix. |
| `core/config.py` | Always | Config dir (`~/.config/cli-web-{app}/`), auth.json path, env var name (`CLI_WEB_{APP}_AUTH_JSON`). |
| `core/client.py` | Always | HTTP client skeleton with correct import (httpx/curl_cffi), `_request()` method with status→exception mapping, auth header injection, rate-limit retry with backoff. Protocol-specific: REST (method-per-endpoint), GraphQL (query template), batchexecute (delegates to rpc/), HTML (httpx + BS4 parse method). |
| `core/rpc/types.py` | batchexecute only | Method ID enum stub, URL constants. |
| `core/rpc/encoder.py` | batchexecute only | Encoder skeleton from notebooklm reference. |
| `core/rpc/decoder.py` | batchexecute only | Decoder skeleton from notebooklm reference. |
| `core/rpc/__init__.py` | batchexecute only | Package init. |
| `utils/helpers.py` | Always | `handle_errors()` context manager, `print_json()`, Windows UTF-8 fix for stdout+stderr. Conditionally: `resolve_partial_id()` (has_partial_ids), `poll_until_complete()` (has_polling), `get_context_value()`/`set_context_value()` (has_context). |
| `utils/output.py` | Always | `format_table()`, `json_error()`, `json_success()`. |
| `__init__.py` | Always | `__version__ = "0.1.0"` |
| `__main__.py` | Always | `python -m cli_web.{app}` support. |

### NOT Generated (agent writes manually)

- `commands/*.py` — too app-specific (business logic)
- `core/auth.py` — login flow varies per site
- `core/models.py` — response shapes are unique
- `<app>_cli.py` — entry point depends on command groups
- `utils/repl_skin.py` — copied from plugin scripts/ (existing process)

### Skill Content Structure

The SKILL.md contains:
1. Input collection instructions (read traffic-analysis.json, derive parameters)
2. Decision matrix (protocol → which files to generate, which patterns to use)
3. Code templates for each file, with `{app}`, `{APP}`, `{AppName}` placeholders
4. Post-generation checklist (verify all files created, no `cli_web/__init__.py`)

### Methodology Skill Changes

In `skills/methodology/SKILL.md` Step B, insert between "Package Structure" section (line ~166) and "Implementation Rules" (line ~169):

```markdown
### Step B.0: Scaffold Core Modules

Before writing implementation code, read `${CLAUDE_PLUGIN_ROOT}/skills/boilerplate/SKILL.md`
and follow its instructions to scaffold the core/ modules. This generates exceptions.py,
client.py skeleton, helpers.py, config.py, and (for batchexecute) the rpc/ subpackage.

After scaffolding, review the generated files and customize `client.py` with actual
endpoint methods from `<APP>.md`.
```

---

## 3. Cross-CLI Consistency Checker Agent

### Location
```
cli-anything-web-plugin/agents/
└── cross-cli-consistency-checker.md
```

### Design

An agent that audits all generated CLIs against current HARNESS conventions. Reports drift — does not auto-fix.

**Frontmatter**:
```yaml
name: cross-cli-consistency-checker
version: 0.1.0
description: >
  Audit all cli-web-* CLIs for convention drift against current HARNESS.md.
  Reports PASS/FAIL per check per CLI. Use periodically or before releases.
tools: [Read, Grep, Glob, Bash]
```

### Plugin Root Discovery

The agent locates the plugin's `scripts/repl_skin.py` (for check #11) by globbing for `**/cli-anything-web-plugin/scripts/repl_skin.py` from the repository root. This avoids depending on `${CLAUDE_PLUGIN_ROOT}` which is not available in agent context.

### Discovery

Finds CLIs by reading `registry.json` at repo root, falling back to glob `*/agent-harness/cli_web/*/__init__.py`.

### Check Matrix

| # | Check | What to look for | Severity |
|---|-------|-----------------|----------|
| 1 | Exception hierarchy | All 5 subtypes present, `to_dict()` on base, `retry_after` on RateLimitError, `status_code` on ServerError | Critical |
| 2 | UTF-8 fix | Both `sys.stdout` AND `sys.stderr` reconfigured in `_cli.py` | Critical |
| 3 | REPL parsing | `shlex.split()` used, not `line.split()` | Critical |
| 4 | REPL dispatch | `cli.main(args=..., standalone_mode=False)` not `**ctx.params` | Critical |
| 5 | Namespace package | `cli_web/__init__.py` does NOT exist | Critical |
| 6 | handle_errors | All commands use context manager | Important |
| 7 | No click.ClickException | No `raise click.ClickException` in commands/ | Important |
| 8 | JSON error format | Errors use `to_dict()` pattern | Important |
| 9 | Auth env var | `CLI_WEB_{APP}_AUTH_JSON` supported (auth CLIs only) | Important |
| 10 | Auth chmod | `os.chmod(auth_file, 0o600)` present (auth CLIs only) | Important |
| 11 | repl_skin.py version | Matches `scripts/repl_skin.py` in plugin | Minor |
| 12 | setup.py namespaces | `find_namespace_packages(include=["cli_web.*"])` | Important |

### Output Format

```
Cross-CLI Consistency Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━
                  ExcH  UTF8  REPL  Disp  NS    HErr  NoClk JSON  Auth  Chmd  Skin  Setup
futbin            PASS  FAIL  PASS  PASS  PASS  PASS  PASS  PASS  N/A   N/A   FAIL  PASS
reddit            PASS  PASS  PASS  PASS  PASS  FAIL  FAIL  PASS  PASS  PASS  PASS  PASS
...

Summary: 3 Critical, 5 Important, 2 Minor findings across 12 CLIs

Critical Issues:
  futbin: UTF-8 fix missing for sys.stderr (futbin_cli.py:12)
  ...
```

### Not In Scope
- Auto-fixing findings (read-only audit)
- Checking test quality (that's the testing skill's job)
- Checking API coverage (that's the gap analyzer's job)

---

## 4. CLI Gap Analyzer Skill

### Location
```
cli-anything-web-plugin/skills/gap-analyzer/
└── SKILL.md
```

### Design

A skill that produces a structured gap report comparing documented API surface vs implemented commands.

**Frontmatter**:
```yaml
name: gap-analyzer
version: 0.1.0
description: >
  Compare implemented CLI commands against <APP>.md API map to find missing
  endpoints, incomplete CRUD, dead client methods, and priority gaps.
  TRIGGER when: "gap analysis", "what's missing", "coverage report",
  "what endpoints are not implemented", or as a sub-step of the refine workflow.
  DO NOT trigger for: "refine" alone (use the /cli-anything-web:refine command).
```

### Process

**Step 1: Parse implemented surface**
- Read all `commands/*.py` files → extract Click command/group names and their decorators
- Read `client.py` → extract all public methods (potential endpoints)
- Build set: `{(resource_group, command_name, client_method)}`

**Step 2: Parse documented surface**
- Read `<APP>.md` → extract endpoint table/list
- Build set: `{(resource_group, verb, endpoint_path, http_method)}`

**Step 3: Diff**
- **Missing commands**: In API map, no corresponding Click command
- **Undocumented commands**: Implemented but not in API map (hallucination risk flag)
- **Dead client methods**: In `client.py` but no command calls them
- **Incomplete CRUD**: Resource has some CRUD ops but missing others the API supports

**Step 4: Priority scoring** (optional, requires `raw-traffic.json`)
- Count endpoint appearances in captured traffic
- HIGH: 5+ hits, MED: 2-4 hits, LOW: 1 hit
- Note: traffic captures are incomplete — endpoints not exercised during capture may be ranked LOW even if important. The report should note this limitation.

**Step 5: Output**
```
Gap Report: cli-web-<app>
━━━━━━━━━━━━━━━━━━━━━━━━━
Coverage: X/Y endpoints (Z%)

Missing (HIGH):
  POST /api/endpoint — description (N hits in traffic)

Missing (MED):
  GET /api/endpoint — description (N hits)

Incomplete CRUD:
  resource: has list ✓, get ✓, missing create ✗, delete ✗

Dead client methods:
  client.some_method() — not called by any command

Undocumented:
  None
```

### Refine Command Changes

In `commands/refine.md` step 3:
- Replace: "Compare known endpoints vs implemented commands"
- With: "Invoke the `gap-analyzer` skill to produce a structured gap report"

Step 4 ("Present gap report") stays the same — the skill output IS the gap report to present.

---

## Files Changed Summary

### New Files (6)
- `cli-anything-web-plugin/agents/traffic-fidelity-reviewer.md`
- `cli-anything-web-plugin/agents/harness-compliance-reviewer.md`
- `cli-anything-web-plugin/agents/output-ux-reviewer.md`
- `cli-anything-web-plugin/agents/cross-cli-consistency-checker.md`
- `cli-anything-web-plugin/skills/boilerplate/SKILL.md`
- `cli-anything-web-plugin/skills/gap-analyzer/SKILL.md`

### Modified Files (3)
- `cli-anything-web-plugin/skills/standards/SKILL.md` — Update Step 1 to reference agent names instead of review-agents.md
- `cli-anything-web-plugin/skills/methodology/SKILL.md` — Add Step B.0 boilerplate scaffold step
- `cli-anything-web-plugin/commands/refine.md` — Update step 3 to invoke gap-analyzer skill

### Deleted Files (1)
- `cli-anything-web-plugin/skills/standards/references/review-agents.md` — Content migrated to agent files
