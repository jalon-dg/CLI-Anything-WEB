---
name: youtube-cli
description: Use cli-web-youtube to search YouTube videos, get video details (views, duration, description, keywords), browse trending content by category, and explore channels. Invoke this skill whenever the user asks about YouTube, searching for videos, video details, YouTube trending, channel info, subscriber counts, or wants to find videos by topic. Always prefer cli-web-youtube over manually fetching the YouTube website.
---

# cli-web-youtube

YouTube CLI — search videos, get details, browse trending, explore channels.

## Quick Start

```bash
pip install -e youtube/agent-harness
cli-web-youtube search videos "python tutorial" --limit 5 --json
cli-web-youtube video get dQw4w9WgXcQ --json
cli-web-youtube channel get @MrBeast --json
```

## Commands

### Search

```bash
cli-web-youtube search videos <query> [--limit N] --json
```

Output: `{"query", "estimated_results", "videos": [{"id", "title", "channel", "channel_id", "views", "duration", "published", "thumbnail", "description", "url"}]}`

### Video

```bash
cli-web-youtube video get <id_or_url> --json
```

Accepts video ID (`dQw4w9WgXcQ`) or full URL (`https://www.youtube.com/watch?v=...`).

Output: `{"id", "title", "channel", "channel_id", "views", "duration_seconds", "description", "keywords", "thumbnail", "is_live", "publish_date", "category", "url"}`

### Trending

```bash
cli-web-youtube trending list [--category now|music|gaming|movies] [--limit N] --json
```

Output: `{"videos": [...], "count", "category"}`

### Channel

```bash
cli-web-youtube channel get <handle_or_url> --json
```

Accepts `@handle`, channel ID (`UC...`), or full URL.

Output: `{"channel_id", "title", "description", "subscriber_count", "video_count", "avatar", "url", "recent_videos": [...]}`

## Agent Patterns

```bash
# Find top Python tutorials
cli-web-youtube search videos "python tutorial" --limit 5 --json | jq '.videos[] | {title, views, url}'

# Get details on a specific video
cli-web-youtube video get rfscVS0vtbw --json

# Check a channel's subscriber count
cli-web-youtube channel get @mkbhd --json | jq '{title, subscriber_count}'
```

## Notes

- No authentication required — all public content
- Uses YouTube's InnerTube API (internal REST, all POST with JSON)
- All commands support `--json` for structured output
- Video IDs are 11 characters (e.g., `dQw4w9WgXcQ`)
- Channel handles start with `@` (e.g., `@MrBeast`)
