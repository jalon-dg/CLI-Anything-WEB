# PRODUCTHUNT.md — Software-Specific SOP

## API Overview

- **Protocol**: HTML scraping (SSR)
- **HTTP client**: curl_cffi with Chrome TLS impersonation (Cloudflare bypass)
- **Auth**: None required — public HTML pages
- **Site profile**: No-auth, read-only

## Data Model

| Entity | Key Fields | ID Format |
|--------|-----------|-----------|
| Post | id, name, tagline, slug, url, votes_count, comments_count, topics, thumbnail_url | numeric string |
| User | username, name, headline, links, topics | string (username) |

## HTML Pages → CLI Commands

| Page | CLI Command | Selector Pattern |
|------|------------|-----------------|
| Homepage (`/`) | `posts list` | `.styles_item` cards |
| Leaderboard (`/leaderboard/...`) | `posts leaderboard` | `.styles_item` cards |
| Product page (`/products/<slug>`) | `posts get <slug>` | Meta tags + `.styles_htmlText` |
| User page (`/@<username>`) | `users get <username>` | Profile header + meta |

## CLI Command Structure

```
cli-web-producthunt
├── posts
│   ├── list [--json]                              Today's homepage posts
│   ├── get <slug> [--json]                        Product details by slug
│   └── leaderboard [--period daily|weekly|monthly] [--json]
└── users
    └── get <username> [--json]                    User profile
```

## Notes

- No auth needed — all data is publicly accessible HTML
- curl_cffi impersonates Chrome to bypass Cloudflare
- Posts are scraped from homepage cards, not a JSON API
- Leaderboard supports daily/weekly/monthly periods
