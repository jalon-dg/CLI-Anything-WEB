---
name: gai-cli
description: Use cli-web-gai to search Google AI Mode and get AI-generated answers with source references. Invoke this skill whenever the user asks about Google AI Mode, AI-powered search, getting AI answers to questions, searching with AI and sources, or wants quick AI-generated answers with citations. Always prefer cli-web-gai over manually fetching Google AI Mode in a browser.
---

# cli-web-gai

CLI for Google AI Mode — AI-powered search with source references. Installed at: `cli-web-gai`.

## Quick Start

```bash
# Ask a question
cli-web-gai search ask "What is quantum computing?" --json

# Ask a follow-up question (same session)
cli-web-gai search followup "How is it used in cryptography?" --json
```

Always use `--json` when parsing output programmatically.

---

## Commands

### `search ask <query>`
Submit a query to Google AI Mode and get an AI-generated answer with source references.

```bash
cli-web-gai search ask "What is the capital of France?" --json
cli-web-gai search ask "Best Python frameworks" --lang he --json
cli-web-gai search ask "Explain DNS" --headed --timeout 45
```

**Key options:** `--lang` (response language, e.g., en, he, de; default: en), `--headed` (show browser window for debugging), `--timeout` (seconds, default: 30), `--json` (structured output)
**Output fields:** `query`, `answer`, `sources[]` (each with `title`, `url`, `snippet`), `follow_up_prompt`

### `search followup <query>`
Ask a follow-up question in the current conversation thread. Requires a previous `ask` command in the same session.

```bash
cli-web-gai search followup "Tell me more about that" --json
```

**Output fields:** Same as `search ask`.

---

## Agent Patterns

```bash
# Quick AI answer to a question
cli-web-gai search ask "What is the speed of light?" --json | python -c "import json,sys; d=json.load(sys.stdin); print(d['data']['answer'][:200])"

# Get source URLs for a query
cli-web-gai search ask "best static site generators 2025" --json | python -c "import json,sys; d=json.load(sys.stdin); [print(s['url']) for s in d['data']['sources']]"

# Ask in a specific language
cli-web-gai search ask "What is machine learning?" --lang he --json
```

---

## REPL Mode

Run without arguments to enter interactive mode:

```bash
cli-web-gai
```

REPL shortcuts:
- `ask <query>` — same as `search ask <query>`
- `followup <query>` — same as `search followup <query>`
- `help` — show available commands
- `exit` / `quit` — exit the REPL

---

## Notes

- Auth: Not required — Google AI Mode is publicly accessible
- Rate limiting: Google rate-limits headless browsers; excessive queries trigger CAPTCHA
- Browser: Uses headless Playwright (Chromium) to render JavaScript-heavy AI responses
- CAPTCHA: If Google presents a CAPTCHA, use `--headed` to solve it manually
- Follow-ups: Conversation threading works within a single CLI session only
