---
name: capture
description: >
  Capture HTTP traffic from web apps using playwright-cli. Includes site fingerprinting
  (framework detection, protection checks, iframe detection, auth detection, API discovery)
  and full traffic recording with tracing and optional HAR output.
  TRIGGER when: "record traffic from", "capture API calls from", "start Phase 1 for",
  "analyze traffic from URL", "assess site", "site fingerprint", "start capture for",
  "open browser for", or any URL is given as the first step of CLI generation.
  DO NOT trigger for: Phase 2 implementation, test writing, or quality validation.
version: 0.3.0
---

# Traffic Capture (Phase 1)

Assess the site, then capture comprehensive HTTP traffic. This skill combines
site assessment with full traffic recording in a single browser session.

---

## CRITICAL EXECUTION RULES

> **NEVER use `run_in_background: true` for ANY playwright-cli command.**
> All playwright-cli commands must run in the foreground with appropriate timeouts.
> Background execution causes task ID tracking failures — the command completes
> before you can read the output. See `references/playwright-cli-commands.md`
> for the timeout table.

> **NEVER use `eval` for complex expressions.** `eval` fails silently on ternaries,
> comma operators, and multi-branch logic with "not well-serializable" errors.
> Use `run-code` instead. See `references/framework-detection.md` for details.

> **ESM context — no `require()`.** `run-code` uses ESM. Use `await import('fs')`
> instead of `require('fs')`. See `references/playwright-cli-commands.md`.

---

## Prerequisites (Hard Gate)

Do NOT start unless:
- [ ] playwright-cli is available (`npx @playwright/cli@latest --version`)
- [ ] Target URL is known

**Default capture method:** playwright-cli tracing (standard workflow below).

**Optional `--mitmproxy` mode:** If the user passed `--mitmproxy` flag to `/cli-anything-web`, use `mitmproxy-capture.py` instead — it provides no body truncation, real-time noise filtering, deduplication, and enhanced metadata (timestamps, cookies, body sizes). Requires `pip install mitmproxy` (Python 3.12+):
```
python ${CLAUDE_PLUGIN_ROOT}/scripts/mitmproxy-capture.py start-proxy --port 8080
npx @playwright/cli@latest open <url> --config=.playwright/cli.proxy.config.json --headed
# ... browse the site as normal (snapshot, click, fill, goto) ...
npx @playwright/cli@latest -s=<app> close
python ${CLAUDE_PLUGIN_ROOT}/scripts/mitmproxy-capture.py stop-proxy --port 8080 -o <app>/traffic-capture/raw-traffic.json
```

If playwright-cli fails, fall back to chrome-devtools-mcp (see HARNESS.md Tool Hierarchy).

### Public API Shortcut

If the target site has a **documented public REST/JSON API** (e.g., Hacker News Firebase API, Dev.to API, Reddit API, Wikipedia API), browser capture is optional:

1. Probe the API endpoints directly with `httpx` or `curl`
2. Save responses as `<app>/traffic-capture/raw-traffic.json`
3. Skip to Phase 2 (methodology)

This applies when:
- API docs exist (OpenAPI/Swagger, developer docs page, `/api/` prefix)
- The API is publicly accessible without browser-specific auth
- Endpoints return JSON (not HTML)

If unsure whether a public API exists, proceed with browser capture as normal.

### Resume from Checkpoint

Before starting, check if a previous capture session exists:

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/capture-checkpoint.py restore <app>
```

If a checkpoint exists, read the `guidance` field and **resume from the last
completed step** instead of starting over. This prevents duplicate work when
sessions are interrupted.

---

## 命令行参数

### Auth Mode 选项

**--auth-mode** (可选):
- `auto` (默认): 自动检测认证方式
- `cookie`: 强制使用 Cookie 模式
- `token`: 强制使用 Token 模式

使用示例：
```bash
/cli-anything-web:record https://example.com --auth-mode cookie
/cli-anything-web:record https://example.com --auth-mode token
```

如果指定了 --auth-mode，则跳过自动检测，直接使用指定模式。

认证检测逻辑详见 [auth-detection.md](references/auth-detection.md)

---

## Step 1: Setup

```bash
# Create output directory
mkdir -p <app>/traffic-capture

# Clear any stale sessions
npx @playwright/cli@latest kill-all 2>/dev/null || true

npx @playwright/cli@latest -s=<app> open <url> --headed --persistent
# Note: heavy SPAs (Next.js, React) may show "TimeoutError: page._snapshotForAI" on open.
# This is non-fatal — verify with: npx @playwright/cli@latest list
#
# IMPORTANT — "Browser opened with pid..." in command output means the daemon
# RE-ATTACHED to the existing browser, NOT that a new session was created.
# Do NOT re-navigate or restart when you see this. The session is still open.
```

> **If `--mitmproxy` mode:** Replace the `open` command above with:
> ```bash
> python ${CLAUDE_PLUGIN_ROOT}/scripts/mitmproxy-capture.py start-proxy --port 8080
> npx @playwright/cli@latest -s=<app> open <url> --config=.playwright/cli.proxy.config.json --headed
> ```
> This starts the proxy first, then opens the browser routed through it.
> All subsequent `snapshot`, `click`, `fill`, `goto` commands work exactly the same.

**Do NOT ask the user to log in yet** — Step 2 will determine if auth is needed.

---

## Step 2: Site Fingerprint (Single Command)

Run the all-in-one site fingerprint command instead of individual eval calls.
This is faster, more reliable, and detects framework + protection + iframes +
auth requirements in one shot.

**Use the script file** — multi-line JS with arrow functions and optional chaining
fails in playwright-cli's single-line command parser. The script file approach
has been tested and works reliably:

```bash
npx @playwright/cli@latest -s=<app> run-code "$(grep -v '^\s*//' ${CLAUDE_PLUGIN_ROOT}/scripts/site-fingerprint.js | tr '\n' ' ')"
```

> **IMPORTANT:** The `site-fingerprint.js` script must be loaded via the command
> above. Do NOT copy-paste the JS inline — it will fail with SyntaxError.
> The `grep -v` strips comments and `tr` joins lines for single-line execution.
```

### Interpret fingerprint results

**Framework:**
- `googleBatch: true` → Google batchexecute RPC protocol. Generate `rpc/` subpackage.
- `nextPages: true` → Next.js Pages Router. Extract `__NEXT_DATA__` + trace `/_next/data/` fetches.
- `nextApp: true` → Next.js App Router. Trace client navigations for RSC payloads.
- `nuxt: true` → Nuxt. Extract `__NUXT__` + trace API calls.
- No framework flags → likely SSR HTML or custom SPA. Check for REST API in probe.

**Protection:**
- `cloudflare: true` → Use `curl_cffi` with `impersonate='chrome'` in generated CLI.
- `awsWaf: true` → Need WAF token cookie via browser. Use curl_cffi for API calls.
- `captcha: true` → Add pause-and-prompt to auth flow.
- `serviceWorker: true` → Site has an active Service Worker that may intercept requests
  and hide them from traces. Note in assessment.md. Generated CLI's auth.py should use
  `service_workers="block"` in browser context. See `references/protection-detection.md`.

**Iframes:**
- `iframeCount > 0` → App is iframe-embedded. **Re-run detection inside the iframe:**

```bash
npx @playwright/cli@latest -s=<app> run-code "async page => {
  const frame = page.frames()[1];
  if (!frame) return { error: 'no iframe found' };
  return await frame.evaluate(() => ({
    framework: {
      nextPages: !!document.getElementById('__NEXT_DATA__'),
      googleBatch: typeof WIZ_global_data !== 'undefined',
      spaRoot: document.querySelector('#app, #root')?.id || null,
      vite: !!document.querySelector('script[type=\"module\"][src*=\"/@vite\"]') || !!document.querySelector('script[type=\"module\"][src*=\"/src/\"]')
    },
    title: document.title,
    bodyPreview: document.body?.textContent?.substring(0, 300) || ''
  }));
}"
```

Common iframe pattern: Google Labs apps (Stitch, MusicFX, ImageFX) embed a
Vite/React SPA in an iframe. Parent has `WIZ_global_data`, iframe has the real app.
See `references/playwright-cli-advanced.md` for iframe interaction patterns.

**Note:** `snapshot` and `click <ref>` auto-resolve iframes. Only use `run-code`
for iframe interaction when built-in commands fail.

### Auth detection (BEFORE exploration)

Check the fingerprint auth fields:

| Condition | Meaning | Action |
|-----------|---------|--------|
| `hasLoginButton && !hasUserMenu` | Login required, not logged in | Ask user to log in NOW |
| `hasUserMenu` | Already logged in | Proceed to capture |
| `!hasLoginButton && !hasUserMenu` | No auth needed (public site) | Skip auth, proceed |

**If auth is needed:**
1. Tell the user: "This site requires login. Please log in in the browser window."
2. Wait for user confirmation
3. Save auth state:
```bash
npx @playwright/cli@latest -s=<app> state-save <app>/traffic-capture/<app>-auth.json
```

**If NO auth is needed:** Skip directly to Step 2b.

### 2b. Classify Site Profile + Check Scope

Based on fingerprint results AND what you see in the UI, classify the site:

| Profile | Auth? | Operations | Exploration Focus |
|---------|-------|-----------|-------------------|
| **Auth + CRUD** | Yes | Create, Read, Update, Delete | Full CRUD per resource |
| **Auth + Generation** | Yes | Generate, Poll, Download | Generation lifecycle + projects |
| **Auth + Read-only** | Yes | Read, Search, Export | Read operations + auth flow |
| **No-auth + CRUD** | No/Optional | Full CRUD | Skip auth, full CRUD |
| **No-auth + Read-only** | No | Read, Search | Minimal capture |

**Check scope (set by cli-anything-web command):**
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/phase-state.py get <app> --key scope
```

- **`scope=partial`**: 这是"特定页面"模式
  - **不要进行站点探索** (跳过 Step 2c Quick API Probe)
  - 直接在当前 URL 页面进行 Step 3 抓取
  - 只捕获页面加载时的 API 请求和用户的简单交互
  - 在 assessment.md 中标记: `scope: partial (single page)`
- **`scope=full` 或未设置**: 执行标准全站抓取流程

### 2c. Quick API Probe (Force SPA Navigation Trick)

Start a SHORT trace, click 3-4 internal links, stop. This reveals hidden API
endpoints that SSR hides on initial page load.

```bash
npx @playwright/cli@latest -s=<app> tracing-start
npx @playwright/cli@latest -s=<app> click <internal-link-1>
npx @playwright/cli@latest -s=<app> click <internal-link-2>
npx @playwright/cli@latest -s=<app> click <internal-link-3>
npx @playwright/cli@latest -s=<app> tracing-stop

# Quick parse to see what endpoints appeared
python ${CLAUDE_PLUGIN_ROOT}/scripts/parse-trace.py .playwright-cli/traces/ --latest --output /tmp/probe.json
```

Check the probe results — what API patterns did you find?
See `references/api-discovery.md` for the priority chain and decision tree.

### 2d. Write Assessment Summary

Create `<app>/traffic-capture/assessment.md` to consolidate all findings:

```markdown
# Site Assessment: <app>

- **URL**: <url>
- **Framework**: <detected framework or "none/custom">
- **Protocol**: <REST / GraphQL / batchexecute / HTML scraping / hybrid>
- **Protection**: <none / cloudflare / captcha / aws-waf / etc.>
- **Auth required**: <yes (type: Google SSO / cookie / JWT / API key) / no>
- **Auth mode**: <detected auth mode> (auto-detected | user-selected | cookie | token)
- **Iframes**: <yes (N frames, app in frame N at <url>) / no>
- **Site profile**: <Auth+CRUD / Auth+Generation / Auth+Read-only / No-auth+CRUD / No-auth+Read-only>
- **Capture scope**: <full (entire site) / partial (single page)>
- **Capture strategy**: <API-first / SSR+API hybrid / batchexecute / HTML scraping / protected-manual>
- **Key observations**: <any quirks, localized UI, rate limits, special patterns>
```

> **Note for partial scope**: If `scope=partial`, only capture what's needed for the single URL. The generated CLI will be a "simplified" version with only the captured functionality.

---

## Step 3: Full Traffic Capture

> **Tip: For complex forms with multiple options/fields, record each scenario separately.**
> For example, if you're capturing a "create order" form:
> - Recording 1: Create order with status=draft
> - Recording 2: Create order with status=published
> - Recording 3: Create order with priority=high
>
> Each recording will be merged into a single CLI command with `--option` flags in Phase 2.

**Important: Check scope first:**
```bash
SCOPE=$(python ${CLAUDE_PLUGIN_ROOT}/scripts/phase-state.py get <app> --key scope 2>/dev/null || echo "full")
```

Now do the capture based on scope:

- **`scope=partial` (Specific Page Mode):**
  - Skip the profile-specific exploration checklist below
  - Just capture the initial page load + any immediately visible API calls
  - Take 1-2 simple interactions (e.g., click a button, fill a small form) if needed
  - **Do NOT navigate to other pages or explore the site**
  - Go directly to Step 4 (Stop, Save, Parse)
  - This is intentionally lightweight — just enough for the single URL

- **`scope=full` (Full Site Mode):**
  - Proceed with the full exploration below

```bash
# Optional: Start HAR recording alongside trace for standard-format capture
# HAR files enable mitmproxy2swagger (auto OpenAPI spec) and third-party analysis tools
npx @playwright/cli@latest -s=<app> run-code "async page => {
  await page.context().routeFromHAR('<app>/traffic-capture/capture.har', {
    update: true,
    updateContent: 'embed',
    updateMode: 'full'
  });
  return 'HAR recording started';
}"

# Start fresh trace for full capture (note the trace ID from output!)
npx @playwright/cli@latest -s=<app> tracing-start
# Output: "trace-<ID>" — record this ID

```

> **If `--mitmproxy` mode:** Skip `tracing-start` and HAR recording above.
> mitmproxy is already capturing all traffic since Step 1 — just proceed
> to the exploration below. Every click, navigation, and form submission
> is automatically recorded by the proxy.

> **HAR recording is optional but recommended.** It produces a standard HAR file
> alongside the trace. This enables `mitmproxy2swagger` to auto-generate an
> OpenAPI spec: `pip install mitmproxy2swagger && mitmproxy2swagger -i capture.har -o api-spec.yaml -p <base-url>`
> The HAR file is saved when the browser context is closed (Step 5).

### Exploration by site profile

Use the profile-specific checklist from Step 2b:

**Auth + CRUD:**
```
For EACH resource visible in the UI:
- [ ] List/browse: navigate to list view
- [ ] Detail: open one item
- [ ] Create: fill form, submit (capture POST body!)
- [ ] Update: edit an item, save
- [ ] Delete: delete a test item
- [ ] Settings/profile: check app settings
- [ ] Export: if available, trigger export/download
```

**Auth + Generation:**
```
- [ ] Dashboard/projects: navigate to project list
- [ ] Open existing project: view editor/canvas
- [ ] Generate new content: type prompt, click generate, WAIT for completion
- [ ] Edit/iterate: modify generation, re-generate
- [ ] Export/download: trigger download of generated content
- [ ] Delete: delete a test project
- [ ] Settings: check model selection, preferences
```

**Auth + Read-only:**
```
- [ ] Main view: navigate to primary content
- [ ] Search/filter: use search functionality
- [ ] Detail pages: open 2-3 different items
- [ ] Pagination: go to page 2 if available
- [ ] Export: if available
```

**No-auth + CRUD:**
```
Same as Auth + CRUD, but skip auth-related captures.
```

**No-auth + Read-only:**
```
- [ ] Homepage: capture initial data
- [ ] Search: try 2-3 different queries
- [ ] Detail pages: open 2-3 items
- [ ] Filters: apply different filters
- [ ] Pagination: check next page
```

### General interaction rules

- **Click by ref (from snapshot) is most reliable:** `snapshot` → note ref → `click <ref>`
- **Refs go stale** — always take a fresh snapshot before clicking
- **For localized UIs** (Hebrew, Arabic, etc.) — use refs or data-testid, not text
- **For iframe-embedded apps** — `snapshot` + `click <ref>` auto-resolves iframes
- **Wait after generation** — if the app generates content async, wait:
  ```bash
  npx @playwright/cli@latest -s=<app> run-code "async page => {
    await page.waitForTimeout(15000);
    return 'waited';
  }"
  ```
- **The trace MUST contain at least one WRITE operation** (POST/PUT/DELETE) unless
  the site is genuinely read-only (see exception below)

**Exception for read-only sites:** If the site is genuinely read-only, the trace
may contain only GET requests. Note "read-only site" in `assessment.md` and proceed.

---

## Step 4: Stop, Save, Parse

```bash
npx @playwright/cli@latest -s=<app> tracing-stop
```

**If `tracing-stop` fails:**
1. Retry once with 15s timeout
2. If it fails again — the trace is lost. Start a new trace (Step 3).
3. **NEVER retry more than twice.** See `references/playwright-cli-tracing.md` for recovery.

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/parse-trace.py \
  .playwright-cli/traces/ --latest \
  --output <app>/traffic-capture/raw-traffic.json

# parse-trace.py now auto-runs analyze-traffic.py and produces:
#   - <app>/traffic-capture/raw-traffic.json (raw request/response data)
#   - <app>/traffic-capture/traffic-analysis.json (auto-detected protocol, auth, endpoints)
#
# The analysis output shows: protocol type, auth pattern, endpoint groups,
# GraphQL operations, batchexecute RPC IDs, and suggested CLI commands.
# Review the analysis — anything marked "unknown" needs manual investigation.

# You can also run the analyzer separately for more detail:
python ${CLAUDE_PLUGIN_ROOT}/scripts/analyze-traffic.py \
  <app>/traffic-capture/raw-traffic.json --summary
```

> **If `--mitmproxy` mode:** Replace everything above with:
> ```bash
> # Stop the proxy and save captured traffic (includes auto-analysis)
> python ${CLAUDE_PLUGIN_ROOT}/scripts/mitmproxy-capture.py stop-proxy \
>   --port 8080 -o <app>/traffic-capture/raw-traffic.json
>
> # The stop-proxy command writes raw-traffic.json directly.
> # Then run the analyzer for the full report:
> python ${CLAUDE_PLUGIN_ROOT}/scripts/analyze-traffic.py \
>   <app>/traffic-capture/raw-traffic.json --summary
> ```
> No `tracing-stop` or `parse-trace.py` needed — mitmproxy already has the data.
> The analysis will include enhanced fields (request_sequence, session_lifecycle,
> endpoint_sizes) that are only available with mitmproxy capture.

---

## Step 4b: Continue Recording (Multiple Scenes)

After parsing, ask the user if they want to record more scenes:

```
# Prompt the user: "继续录制其他场景吗？(y/n)"
# If yes: go back to Step 3 (start new trace)
# If no: proceed to Step 5 (close)

# IMPORTANT: If continuing, save the scene name for this recording first
python -c "
import json
from pathlib import Path

scenes_file = Path('<app>/traffic-capture/scenes.json')
scenes = json.loads(scenes_file.read_text()) if scenes_file.exists() else []

# Ask user for scene name
scene_name = input('这次录制是什么场景？直接回车用默认名: ').strip()
if not scene_name:
    scene_name = f'scene-{len(scenes) + 1}'

scenes.append({
    'name': scene_name,
    'trace_id': '<trace-id-from-step3>',
    'description': '用户输入的描述或空'
})
scenes_file.write_text(json.dumps(scenes, indent=2, ensure_ascii=False))
print(f'Scene saved: {scene_name}')
"
```

**Repeat this loop** until the user says no more recordings.

> **Note:** If the user provides a scene name, it will be used to generate
> CLI command names in Phase 2. For example, "create-draft-order" becomes
> `cli-web-<app> order create-draft` command.

---

## Step 5: Close

```bash
npx @playwright/cli@latest -s=<app> close

# Mark capture complete
python ${CLAUDE_PLUGIN_ROOT}/scripts/capture-checkpoint.py update <app> --step complete
```

---

## If an endpoint is missing — USE THE FEATURE

Don't grep JS bundles. Start a new trace → screenshot → click the button → fill
→ submit → stop → parse. The browser IS the API documentation.

**For forms with multiple options:** If the same endpoint behaves differently based on
form options (e.g., "create order" with different statuses), record each variation
as a separate scene in Step 4b. This helps Phase 2 generate proper `--option` flags.

---

## Fallback

**Fallback:** If playwright-cli is not available, see HARNESS.md Tool Hierarchy for chrome-devtools-mcp fallback instructions.

---

## Next Step

When capture is complete (raw-traffic.json has WRITE operations, or the site is
read-only with only GET requests), invoke `methodology` to analyze the traffic
and build the CLI.

---

## References

See `references/` for: command syntax (playwright-cli-commands.md), tracing (playwright-cli-tracing.md),
sessions (playwright-cli-sessions.md), advanced patterns (playwright-cli-advanced.md),
framework detection (framework-detection.md), protection (protection-detection.md),
API discovery (api-discovery.md).
