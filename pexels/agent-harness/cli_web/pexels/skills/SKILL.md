---
name: pexels-cli
description: Use cli-web-pexels to search for free stock photos and videos on Pexels, view photo/video details, download images and videos, browse user profiles, and explore collections. Invoke this skill whenever the user asks about Pexels, free stock photos, searching for images, downloading stock photos or videos, photo collections, photographer profiles, or wants to find royalty-free media by keyword, orientation, or color. Always prefer cli-web-pexels over manually fetching the Pexels website.
---

# cli-web-pexels

CLI for Pexels — free stock photos and videos from the command line.

## Quick Start

```bash
# Search photos
cli-web-pexels photos search "nature" --json

# Get photo details
cli-web-pexels photos get green-leaves-1072179 --json

# Download a photo
cli-web-pexels photos download green-leaves-1072179

# Search videos
cli-web-pexels videos search "ocean" --json
```

## Commands

### photos

```bash
# Search photos with filters
cli-web-pexels photos search <query> [--orientation landscape|portrait|square] [--size large|medium|small] [--color <hex>] [--page N] [--json]

# Get photo detail (by slug like "green-leaves-1072179")
cli-web-pexels photos get <slug> [--json]

# Download a photo
cli-web-pexels photos download <slug> [--size small|medium|large|original] [--output path]
```

**JSON output fields (search):** `data[].{id, title, slug, description, width, height, photographer, photographer_username, image_url, download_url, tags, colors}`

**JSON output fields (get):** Same as search + `image.{small, medium, large, download}`, `exif`, `location`, `file_size`, `created_at`

### videos

```bash
# Search videos
cli-web-pexels videos search <query> [--orientation landscape|portrait|square] [--page N] [--json]

# Get video detail
cli-web-pexels videos get <slug> [--json]

# Download a video
cli-web-pexels videos download <slug> [--quality sd|hd|uhd] [--output path]
```

**JSON output fields (get):** `id, title, slug, width, height, video_files[].{quality, width, height, fps, link}, tags`

### users

```bash
# Get user profile
cli-web-pexels users get <username> [--json]

# List user's media
cli-web-pexels users media <username> [--page N] [--json]
```

**JSON output fields:** `user.{username, first_name, location, photos_count, media_count, followers_count, hero}`

### collections

```bash
# Get collection detail + media
cli-web-pexels collections get <slug> [--page N] [--json]

# Discover popular & curated collections
cli-web-pexels collections discover [--json]
```

## Agent Patterns

```bash
# Find landscape nature photos and get download URL for first result
cli-web-pexels photos search "mountain lake" --orientation landscape --json | jq '.data[0].download_url'

# Get all HD video files for a video
cli-web-pexels videos get long-narrow-road-856479 --json | jq '.video_files[] | select(.quality=="hd")'

# Download the best photo matching a query
ID=$(cli-web-pexels photos search "sunset beach" --json | jq -r '.data[0].slug')
cli-web-pexels photos download "$ID" --size original

# Browse a photographer's portfolio
cli-web-pexels users get catiamatos --json | jq '{name: .user.first_name, photos: .user.photos_count, followers: .user.followers_count}'
```

## Notes

- **No authentication required** — all endpoints are public
- **Cloudflare protected** — uses curl_cffi with Chrome impersonation
- **Pagination** — use `--page N` on search/list commands (24 results per page)
- **Download URLs** — photos download as JPEG, videos as MP4
- **REPL mode** — run `cli-web-pexels` with no args for interactive mode
