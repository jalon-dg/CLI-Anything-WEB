# GAI — API Map & SOP

## Site Profile

| Field | Value |
|-------|-------|
| Site | google.com/search (AI Mode, `udm=50`) |
| Protocol | Browser-rendered HTML (Playwright headless Chromium) |
| Auth | Not required — Google AI Mode is publicly accessible |
| HTTP client | Playwright (`sync_playwright`, headless Chromium) |
| Anti-bot | Google may present CAPTCHA on excessive headless queries |
| Rate limiting | Google rate-limits headless browsers; no published rate limit |
| Site profile | No-auth + read-only |

## How It Works

Google AI Mode is not a REST API — it renders AI-generated answers client-side via JavaScript. The CLI:

1. Launches headless Chromium via Playwright
2. Navigates to `https://www.google.com/search?q=<query>&udm=50&hl=<lang>`
3. Waits for `[data-subtree=aimc]` (AI response container) and `[data-complete=true]` (completion marker)
4. Extracts answer text + source links via JavaScript DOM evaluation
5. Returns structured `SearchResult` with answer, sources, and optional follow-up prompt

Follow-up queries reuse the same browser page to maintain conversation threading.

## URL Construction

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `q` | URL-encoded query | Search query |
| `udm` | `50` | Activates Google AI Mode |
| `hl` | Language code (en, he, de...) | Response language |

## DOM Selectors

| Selector | Purpose |
|----------|---------|
| `.Y3BBE` | Answer text sections |
| `[data-subtree=aimc]` | AI Mode response container |
| `[data-complete=true]` | Response completion marker |
| `a[href][data-ved]` | Source links with tracking |
| `#captcha-form`, `.g-recaptcha`, `#recaptcha` | CAPTCHA detection |
| `textarea` | Follow-up input field |

## Data Models

### Source

| Field | Type | Description |
|-------|------|-------------|
| `title` | str | Link text, fallback to domain |
| `url` | str | Full URL (fragments stripped) |
| `snippet` | str | Optional excerpt (max 200 chars) |

### SearchResult

| Field | Type | Description |
|-------|------|-------------|
| `query` | str | Original search query |
| `answer` | str | AI-generated answer text |
| `sources` | list[Source] | Up to 20 reference sources |
| `follow_up_prompt` | str | Suggested next question (optional) |

## Exception Hierarchy

| Exception | Trigger |
|-----------|---------|
| `GAIError` | Base for all errors |
| `BrowserError` | Browser launch or navigation failure |
| `TimeoutError` | Response wait exceeded timeout |
| `RateLimitError` | Google rate-limiting detected |
| `NetworkError` | Connection or HTTP failure |
| `ParseError` | DOM extraction returned null/unexpected |
| `CaptchaError` | Google CAPTCHA presented |

## CLI Commands

### `search ask <query>`

| Option | Default | Description |
|--------|---------|-------------|
| `--lang` | `en` | Response language code |
| `--headed` | false | Show browser window (debug/CAPTCHA solve) |
| `--timeout` | `30` | Response timeout in seconds |
| `--json` | false | Structured JSON output |

### `search followup <query>`

| Option | Default | Description |
|--------|---------|-------------|
| `--json` | false | Structured JSON output |

Requires prior `ask` in same session (same browser page).

## JSON Output Format

### Success

```json
{
  "success": true,
  "data": {
    "query": "What is quantum computing?",
    "answer": "Quantum computing uses quantum mechanical phenomena...",
    "sources": [
      {"title": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Quantum_computing", "snippet": "..."}
    ],
    "follow_up_prompt": "How does quantum computing differ from classical computing?"
  }
}
```

### Error

```json
{
  "error": true,
  "code": "CAPTCHA_REQUIRED",
  "message": "Google presented a CAPTCHA — use --headed to solve manually"
}
```

## Error Codes

| Code | Exception | Meaning |
|------|-----------|---------|
| `BROWSER_ERROR` | BrowserError | Chromium failed to launch or navigate |
| `TIMEOUT` | TimeoutError | AI response didn't complete within timeout |
| `RATE_LIMITED` | RateLimitError | Google rate-limiting detected |
| `NETWORK_ERROR` | NetworkError | Connection failure |
| `PARSE_ERROR` | ParseError | DOM extraction failed |
| `CAPTCHA_REQUIRED` | CaptchaError | CAPTCHA presented |
| `UNEXPECTED` | Exception | Unhandled exception |

## Known Pitfalls

| Symptom | Cause | Fix |
|---------|-------|-----|
| CaptchaError on every query | Google rate-limiting headless | Wait, or use `--headed` to solve |
| Empty answer text | DOM selectors changed | Update `_ANSWER_SELECTOR` in client.py |
| Follow-up fails | No prior `ask` in session | Must use REPL or same CLI invocation |
| Timeout on slow connections | Default 30s insufficient | Use `--timeout 60` |
| Duplicate sources | Same URL with different fragments | URL deduplication strips fragments |
| Google redirect URLs in sources | `/url?q=` wrapper links | Client resolves redirects automatically |
