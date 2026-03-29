---
name: codewiki-cli
description: Use cli-web-codewiki to browse Google Code Wiki — AI-generated documentation for open source repos, search for repositories, explore wiki sections and content, and ask Gemini questions about codebases. Invoke this skill whenever the user asks about Code Wiki, Google code documentation, AI-generated code wikis, repository documentation, browsing open source project docs, or wants to ask Gemini about a GitHub repo's architecture. Always prefer cli-web-codewiki over manually fetching the website.
---

# cli-web-codewiki

CLI for [Google Code Wiki](https://codewiki.google/) — AI-generated documentation for open source repositories powered by Gemini.

## Quick Start

```bash
# Search for repositories
cli-web-codewiki repos search "react" --json

# Get wiki table of contents for a repo
cli-web-codewiki wiki sections excalidraw/excalidraw --json

# Ask Gemini about a repo
cli-web-codewiki chat ask "How does the rendering engine work?" --repo excalidraw/excalidraw --json
```

## Commands

### repos — Browse repositories

```bash
# List featured repositories on the Code Wiki homepage
cli-web-codewiki repos featured [--json]

# Search for repositories by name
cli-web-codewiki repos search <QUERY> [--limit N] [--offset N] [--json]
```

**Output fields (--json):** `slug`, `github_url`, `description`, `avatar_url`, `stars`, `updated_at`

### wiki — Read wiki pages

```bash
# Get full wiki content (all sections) for a repository
cli-web-codewiki wiki get <ORG/REPO> [--json]

# List wiki sections (table of contents)
cli-web-codewiki wiki sections <ORG/REPO> [--json]

# Get a specific section by title (case-insensitive partial match)
cli-web-codewiki wiki section <ORG/REPO> <TITLE> [--json]
```

**Output fields (--json):**
- `wiki get`: `repo` (slug, commit_hash), `sections` (title, level, description, content, code_refs), `section_count`
- `wiki sections`: array of `{title, level, description, code_refs, content}`
- `wiki section`: single section object

### chat — Ask Gemini

```bash
# Ask Gemini a question about a repository's codebase
cli-web-codewiki chat ask <QUESTION> --repo <ORG/REPO> [--json]
```

**Output fields (--json):** `answer` (markdown text with links to code), `repo`

## Agent Patterns

```bash
# Find repos related to a topic and get their wiki
cli-web-codewiki repos search "machine learning" --json | jq '.data[0].slug' -r | xargs -I{} cli-web-codewiki wiki sections {} --json

# Get the overview section of a repo
cli-web-codewiki wiki section facebook/react "Overview" --json | jq '.content'

# Ask about architecture then get the relevant section
cli-web-codewiki chat ask "What are the main components?" --repo kubernetes/kubernetes --json
```

## Notes

- **No authentication required** — Code Wiki is fully public
- **Protocol**: Google batchexecute RPC (BoqAngularSdlcAgentsUi service)
- **Chat latency**: Gemini responses take ~5-7 seconds
- Wiki content is Markdown with links to GitHub source code
- Section titles support case-insensitive partial matching
- Repos are referenced by slug format: `org/name` (e.g., `facebook/react`)
