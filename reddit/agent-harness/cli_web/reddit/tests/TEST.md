# TEST.md — cli-web-reddit Test Plan & Results

## Part 1: Test Plan

### Test Inventory

| File | Tests | Layer |
|------|-------|-------|
| `test_core.py` | 47 | Unit (mocked HTTP) + Click integration |
| `test_e2e.py` | 19 | Live API + subprocess |
| **Total** | **66** | |

### Unit Tests (test_core.py)

**TestExceptionHierarchy (9 tests)**
- All exceptions inherit from RedditError
- RateLimitError has retry_after (defaults to None)
- ServerError has status_code (defaults to 500)

**TestClientErrorMapping (8 tests)**
- 404 → NotFoundError
- 429 → RateLimitError (with and without retry-after header)
- 500/503 → ServerError with status_code
- Connection error → NetworkError
- Successful JSON response parsing
- Generic 4xx → RedditError

**TestModels (9 tests)**
- format_post_summary: extracts fields, handles missing data
- format_subreddit_info: subscribers, name, type
- format_user_info: karma, verification
- format_comment: body, depth, is_submitter
- extract_listing_posts: pagination cursor, filters non-t3 children, empty listings

**TestHelpers (14 tests)**
- json_error format with extra fields
- truncate: short, long, None, empty string
- handle_errors exit codes: NotFoundError→1, ServerError→2, NetworkError→2, RateLimitError→1, KeyboardInterrupt→130
- JSON mode error output for each exception type

**TestCLIClick (7 tests)**
- --version flag
- --help shows all command groups
- feed hot --json with mocked client
- feed new --json with mocked client
- search posts --json with mocked client
- JSON error output on NotFoundError
- JSON error output on NetworkError

### E2E Tests (test_e2e.py)

**TestFeedLive (4 tests)**
- feed hot: verify posts with required fields (id, title, author, score)
- feed top: time filter works (day)
- feed popular: returns posts from r/popular
- pagination: cursor-based pagination returns different posts

**TestSubredditLive (4 tests)**
- sub posts: fetch r/python posts
- sub info: verify name, subscribers, type fields
- sub rules: verify rules list returned
- list-get roundtrip: list posts → get one by ID → verify fields match

**TestSearchLive (2 tests)**
- search posts: keyword search returns results
- search subreddits: subreddit search returns results with names

**TestUserLive (2 tests)**
- user about: verify u/spez profile fields
- user posts: verify user submissions returned

**TestCLISubprocess (7 tests)**
- --help: shows all command groups
- --version: shows 0.1.0
- feed hot --json: valid JSON with posts array
- search posts --json: search results with query
- sub info --json: subreddit details
- user info --json: user profile
- Human-readable table output (non-JSON)

Subprocess tests use `_resolve_cli("cli-web-reddit")` pattern with Windows UTF-8 encoding.

---

## Part 2: Test Results

**Date:** 2026-03-24
**Environment:** Windows 11, Python 3.12.8, curl_cffi

### Unit Tests
```
47 passed in 0.57s
```

### E2E + Subprocess Tests
```
19 passed in 19.14s
```

### Summary

| Metric | Value |
|--------|-------|
| Total tests | 66 |
| Passed | 66 |
| Failed | 0 |
| Pass rate | 100% |
| Unit test time | 0.57s |
| E2E test time | 19.14s |
