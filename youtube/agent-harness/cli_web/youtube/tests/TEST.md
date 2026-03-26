# TEST.md — cli-web-youtube

## Part 1: Test Plan

### Test Files
- `test_core.py` — 28 unit tests (mocked HTTP, no network)

### Unit Test Coverage

#### Models (5 tests)
- `format_video_from_renderer` — extracts all fields from videoRenderer
- `format_video_from_renderer` — handles empty renderer
- `format_video_detail` — extracts full detail with microformat
- `format_video_detail` — handles missing microformat
- `format_channel` — extracts pageHeaderRenderer format

#### Exceptions (7 tests)
- `YouTubeError.to_dict()` returns structured JSON
- `AuthError` has code AUTH_EXPIRED
- `RateLimitError.to_dict()` includes retry_after
- `ServerError` stores status_code
- `NotFoundError`, `ParseError`, `NetworkError` have correct codes

#### Helpers (4 tests)
- `handle_errors` exits 1 on YouTubeError
- `handle_errors` exits 1 on unexpected error
- `handle_errors` JSON mode outputs structured error
- `handle_errors` JSON mode includes retry_after for RateLimitError

#### Client (5 tests, mocked httpx)
- Search returns videos list with estimated_results
- Video detail returns full info
- 404 raises NotFoundError
- 429 raises RateLimitError with retry_after
- 500 raises ServerError with status_code

#### CLI Click (7 tests)
- `--help` lists all command groups
- `--version` shows 0.1.0
- `search --help` shows videos subcommand
- `video --help` shows get subcommand
- `search videos` returns JSON with query + videos
- `video get` returns JSON with video details
- `video get` extracts ID from full YouTube URL

---

## Part 2: Test Results

### Run Date: 2026-03-26
### Pass Rate: 100% (28/28)

```
test_core.py::TestModels::test_format_video_from_renderer PASSED
test_core.py::TestModels::test_format_video_from_renderer_empty PASSED
test_core.py::TestModels::test_format_video_detail PASSED
test_core.py::TestModels::test_format_video_detail_no_microformat PASSED
test_core.py::TestModels::test_format_channel_page_header PASSED
test_core.py::TestExceptions::test_youtube_error_to_dict PASSED
test_core.py::TestExceptions::test_auth_error_code PASSED
test_core.py::TestExceptions::test_rate_limit_to_dict_includes_retry_after PASSED
test_core.py::TestExceptions::test_server_error_stores_status_code PASSED
test_core.py::TestExceptions::test_not_found_error PASSED
test_core.py::TestExceptions::test_parse_error PASSED
test_core.py::TestExceptions::test_network_error PASSED
test_core.py::TestHelpers::test_handle_errors_youtube_error_exits_1 PASSED
test_core.py::TestHelpers::test_handle_errors_unexpected_exits_1 PASSED
test_core.py::TestHelpers::test_handle_errors_json_mode_outputs_json PASSED
test_core.py::TestHelpers::test_handle_errors_json_mode_rate_limit PASSED
test_core.py::TestClientMocked::test_search_returns_videos PASSED
test_core.py::TestClientMocked::test_video_detail_returns_info PASSED
test_core.py::TestClientMocked::test_404_raises_not_found PASSED
test_core.py::TestClientMocked::test_429_raises_rate_limit PASSED
test_core.py::TestClientMocked::test_500_raises_server_error PASSED
test_core.py::TestCLIClick::test_help PASSED
test_core.py::TestCLIClick::test_version PASSED
test_core.py::TestCLIClick::test_search_help PASSED
test_core.py::TestCLIClick::test_video_help PASSED
test_core.py::TestCLIClick::test_search_json PASSED
test_core.py::TestCLIClick::test_video_get_json PASSED
test_core.py::TestCLIClick::test_video_get_extracts_id_from_url PASSED

28 passed in 0.24s
```
