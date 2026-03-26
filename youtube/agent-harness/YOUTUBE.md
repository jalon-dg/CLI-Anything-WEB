# YOUTUBE.md — Software-Specific SOP

## API Overview

- **Protocol**: InnerTube REST API (all POST with JSON body)
- **Base URL**: `https://www.youtube.com/youtubei/v1`
- **Auth**: Not required for public content
- **HTTP client**: httpx (no Cloudflare protection)
- **Site profile**: No-auth, read-only

## InnerTube API Context

All requests require an InnerTube context object:

```json
{
  "context": {
    "client": {
      "clientName": "WEB",
      "clientVersion": "2.20260326.01.00",
      "hl": "en",
      "gl": "US"
    }
  }
}
```

API key: Not required for public endpoints.

## Data Model

| Entity | Key Fields | ID Format |
|--------|-----------|-----------|
| Video | videoId, title, author, viewCount, lengthSeconds, description, keywords, thumbnail | string (11 chars) |
| Channel | channelId, title, description, subscriberCount, videoCount, thumbnail | string (UC prefix) |
| SearchResult | videoId, title, channel, views, duration, publishedTime | string |

## InnerTube Endpoints → CLI Commands

| Endpoint | CLI Command | POST Body Key |
|----------|------------|---------------|
| `POST /youtubei/v1/search` | `search <query>` | `query` |
| `POST /youtubei/v1/player` | `video get <id>` | `videoId` |
| `POST /youtubei/v1/browse` (FEtrending) | `trending list` | `browseId=FEtrending` |
| `POST /youtubei/v1/browse` (channel) | `channel get <handle>` | `browseId` from channel resolve |

## Response Parsing

### Search Response
```
response.contents
  .twoColumnSearchResultsRenderer.primaryContents
  .sectionListRenderer.contents[0]
  .itemSectionRenderer.contents[]
    .videoRenderer  → extract video data
    .channelRenderer → extract channel data
```

### Player Response
```
response.videoDetails  → title, videoId, author, viewCount, lengthSeconds, description, keywords
response.microformat.playerMicroformatRenderer → publishDate, category, thumbnail
```

### Browse (Trending) Response
```
response.contents.twoColumnBrowseResultsRenderer.tabs[0]
  .tabRenderer.content.sectionListRenderer.contents[]
    .itemSectionRenderer.contents[]
      .videoRenderer → extract video data
```

## CLI Command Structure

```
cli-web-youtube
├── search <query> [--limit N] [--json]           Search videos
├── video get <id> [--json]                        Video details
├── trending list [--json]                         Trending videos
└── channel get <handle> [--json]                  Channel info + recent videos
```

## Notes

- No auth needed — all public content
- InnerTube API is internal but stable (used by all YouTube clients)
- All endpoints are POST with JSON body (not GET)
- Response structures are deeply nested — careful parsing needed
- curl_cffi not needed (no Cloudflare)
