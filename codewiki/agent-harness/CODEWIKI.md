# CODEWIKI.md — Software-Specific SOP

## Overview
- **URL**: https://codewiki.google/
- **Protocol**: Google batchexecute (service: BoqAngularSdlcAgentsUi)
- **Auth**: None (fully public, no login required)
- **Site profile**: No-auth + Read-only
- **HTTP library**: httpx (no anti-bot protection)

## RPC Endpoint
```
POST https://codewiki.google/_/BoqAngularSdlcAgentsUi/data/batchexecute
```

Query params:
- `rpcids`: RPC method ID
- `source-path`: "/" (constant)
- `hl`: "en" (language)
- `rt`: "c" (constant)

No CSRF token, no session ID, no auth cookies needed.

## RPC Methods

### nm8Fsb — Featured Repositories
- **Params**: `[]`
- **Response**: `[repos_array]`
  - Each repo: `[slug, null, null, [null, github_url], null, [description, avatar_url, stars]]`

### VSX6ub — Wiki Page Content
- **Params**: `[github_url]` (e.g., `["https://github.com/excalidraw/excalidraw"]`)
- **Response**: `[[repo_info, sections_array, null, null, timestamps], [metadata, has_wiki, type]]`
  - `repo_info`: `[slug, commit_hash]`
  - `sections_array`: List of sections, each: `[title, level, description, code_refs, content_markdown]`
    - `level`: 1=top section, 2=subsection, 3=sub-subsection
    - `content_markdown`: Markdown with links to code files and wiki sections
  - `timestamps`: `[seconds, nanos]`
  - `metadata`: `[null, github_url]`

### vyWDAf — Search Repositories
- **Params**: `[query, page_size, query, offset]`
  - `page_size`: default 25
  - `offset`: 0 for first page
- **Response**: `[repos_array]`
  - Each repo: `[slug, null, 3, [null, github_url], [ts_seconds, ts_nanos], [description, avatar_url, stars, display_name]]`

### EgIxfe — Gemini Chat
- **Params**: `[messages, repo_context]`
  - `messages`: `[[text, "user"], [text, "model"], ...]` (conversation history)
  - `repo_context`: `[null, github_url]`
- **Response**: `[markdown_response]`
  - Contains Markdown with wiki section links and code file links
  - Response time: ~6.5s (Gemini inference)

## CLI Command Structure

```
cli-web-codewiki
├── repos
│   ├── featured           # List featured repos
│   └── search <query>     # Search repos (--limit, --offset)
├── wiki
│   ├── get <repo>         # Get full wiki content
│   ├── sections <repo>    # List wiki sections (TOC)
│   └── section <repo> <title>  # Get specific section content
├── chat
│   └── ask <question> --repo <repo>  # Ask Gemini about a repo
└── (REPL mode when no subcommand)
```

## Data Model

### Repository
- `slug`: "org/name" format
- `github_url`: full GitHub URL
- `description`: text
- `avatar_url`: GitHub avatar
- `stars`: integer
- `commit_hash`: (wiki pages only) commit the wiki was generated from
- `updated_at`: timestamp

### WikiSection
- `title`: section heading
- `level`: 1-3 (hierarchy depth)
- `description`: brief summary
- `code_refs`: list of file paths (or null)
- `content`: markdown text

### ChatMessage
- `text`: message content
- `role`: "user" or "model"
