# PEXELS.md — Software-Specific SOP

## Overview
Pexels is a free stock photo and video platform. No authentication required.
Read-only site — no write operations.

## Protocol
SSR HTML + embedded JSON (`__NEXT_DATA__` from Next.js Pages Router).
All data fetched via HTTP GET of page HTML, then parsed from `__NEXT_DATA__` script tag.

## Auth
None required. Public site.

## API Map

### SSR Pages (fetch HTML → parse `__NEXT_DATA__`)

| URL Pattern | Page Route | Data Location | Pagination |
|------------|------------|---------------|------------|
| `/search/{query}/` | `/search/[query]` | `pageProps.initialData.data` | `?page=N` |
| `/search/videos/{query}/` | `/search/videos/[query]` | `pageProps.initialData.data` | `?page=N` |
| `/photo/{slug}/` | `/photo/[slug]` | `pageProps.medium` | N/A |
| `/video/{slug}/` | `/video/[slug]` | `pageProps.medium` | N/A |
| `/@{username}/` | `/user/[slug]` | `pageProps.user`, `pageProps.firstPageOfMedia` | `?page=N` |
| `/collections/{slug}/` | `/collections/[slug]` | `pageProps.collection`, `pageProps.initialData` | `?page=N` |
| `/discover/` | `/discover` | `pageProps.initialData` | N/A |

### Internal JSON APIs

| Endpoint | Returns |
|----------|---------|
| `/en-us/api/v3/search/suggestions/{query}?` | Search autocomplete suggestions |

### Search Filters (query params)
- `orientation`: landscape, portrait, square
- `size`: large, medium, small
- `color`: hex color or name
- `page`: 1-based pagination

### Download URLs (direct, no auth)
- Photos: `images.pexels.com/photos/{id}/pexels-photo-{id}.jpeg?cs=srgb&dl=...`
- Videos: `videos.pexels.com/video-files/{id}/{id}-{quality}_{w}x{h}_{fps}fps.mp4`

## Data Models

### Photo
```
id, slug, title, description, alt, width, height, aspect_ratio, license
image: {small, medium, large, download, download_link}
user: {id, username, first_name, last_name, avatar}
tags: [{name, search_term}]
main_color, colors, created_at
```

### Video
```
Same base fields as Photo, plus:
video: {src, preview_src, thumbnail, download, download_link, video_files}
video_files: [{file_type, quality, width, height, fps, link, download_link}]
```

### User
```
id, username, first_name, last_name, slug, location, bio, avatar
photos_count, media_count, followers_count, badges, hero
```

### Collection
```
id, title, description, slug
collection_media_count, photos_count, videos_count
users, preview_images
```

## CLI Command Design

```
cli-web-pexels
├── photos
│   ├── search <query> [--orientation] [--size] [--color] [--page] [--json]
│   ├── get <id-or-slug> [--json]
│   └── download <id-or-slug> [--output] [--size]
├── videos
│   ├── search <query> [--orientation] [--page] [--json]
│   ├── get <id-or-slug> [--json]
│   └── download <id-or-slug> [--quality] [--output]
├── users
│   ├── get <username> [--json]
│   └── media <username> [--page] [--json]
├── collections
│   ├── get <slug> [--page] [--json]
│   └── discover [--json]
└── (REPL default when no subcommand)
```
