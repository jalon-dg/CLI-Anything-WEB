# TEST.md — cli-web-pexels

## Part 1: Test Plan

### Test Files

| File | Tests | Layer |
|------|-------|-------|
| `test_core.py` | 30 | Unit (mocked HTTP) |
| `test_e2e.py` | 19 | Live E2E + Subprocess |
| **Total** | **49** | |

### Unit Tests (test_core.py)

**Exception hierarchy (11 tests):**
- PexelsError base class inheritance
- RateLimitError stores retry_after, defaults to None
- ServerError stores status_code, defaults to 500
- raise_for_status maps: 200→noop, 404→NotFoundError, 429→RateLimitError, 500→ServerError
- error_code_for returns correct codes for known/unknown types

**Client parsing (5 tests):**
- _get_page extracts pageProps from __NEXT_DATA__ (mocked curl_cffi)
- _get_page raises ParseError on missing __NEXT_DATA__
- _check_status raises correct exceptions for 404, 429, 503

**Normalizers (4 tests):**
- _normalize_photo: extracts id, title, photographer, image_url, tags
- _normalize_video_detail: includes video_files array with quality/link
- _normalize_user: extracts username, photos_count, followers_count
- _normalize_collection: extracts title, media_count, slug

**Helpers (7 tests):**
- sanitize_filename: removes invalid chars, handles empty/whitespace, truncates
- handle_errors: exits 1 for PexelsError, exits 2 for unknown, JSON error output

**Output (3 tests):**
- print_json produces valid JSON
- print_pagination shows page info
- print_pagination silent on empty input

### E2E Live Tests (test_e2e.py — TestPexelsLive)

All tests make real network calls via curl_cffi (Cloudflare bypass):

- **Photo search**: query "nature", verify results > 0, verify fields
- **Photo search with filters**: orientation=landscape
- **Photo search pagination**: page 2, verify pagination.current_page == 2
- **Photo detail**: get photo 1072179, verify id, image.download URL
- **Video search**: query "ocean", verify video type
- **Video detail**: verify video_files array with download links
- **User profile**: "pixabay", verify photos_count > 0
- **User media**: verify media list non-empty
- **Collection detail**: "spring-aesthetic-fvku5ng", verify title, media_count
- **Discover page**: verify popular collections exist
- **Search suggestions**: "cat", verify returns string list
- **Not found**: verify NotFoundError raised

### Subprocess Tests (test_e2e.py — TestCLISubprocess)

Tests run cli-web-pexels as installed binary via _resolve_cli():

- --help: exit 0, "photos" and "videos" in output
- --version: "1.0.0" in output
- photos search --json: valid JSON with data array
- photos get --json: valid JSON with id field
- videos search --json: valid JSON with results array
- users get --json: valid JSON with user.username
- collections discover --json: valid JSON with popular array

---

## Part 2: Test Results

**Date:** 2026-03-24
**Pass rate:** 49/49 (100%)

```
cli_web/pexels/tests/test_core.py::TestExceptionHierarchy::test_pexels_error_is_base PASSED
cli_web/pexels/tests/test_core.py::TestExceptionHierarchy::test_rate_limit_error_stores_retry_after PASSED
cli_web/pexels/tests/test_core.py::TestExceptionHierarchy::test_rate_limit_error_retry_after_none PASSED
cli_web/pexels/tests/test_core.py::TestExceptionHierarchy::test_server_error_stores_status_code PASSED
cli_web/pexels/tests/test_core.py::TestExceptionHierarchy::test_server_error_default_status PASSED
cli_web/pexels/tests/test_core.py::TestExceptionHierarchy::test_raise_for_status_404 PASSED
cli_web/pexels/tests/test_core.py::TestExceptionHierarchy::test_raise_for_status_429 PASSED
cli_web/pexels/tests/test_core.py::TestExceptionHierarchy::test_raise_for_status_500 PASSED
cli_web/pexels/tests/test_core.py::TestExceptionHierarchy::test_raise_for_status_200_noop PASSED
cli_web/pexels/tests/test_core.py::TestExceptionHierarchy::test_error_code_for_known PASSED
cli_web/pexels/tests/test_core.py::TestExceptionHierarchy::test_error_code_for_unknown PASSED
cli_web/pexels/tests/test_core.py::TestClientParsing::test_get_page_extracts_page_props PASSED
cli_web/pexels/tests/test_core.py::TestClientParsing::test_get_page_raises_parse_error_no_next_data PASSED
cli_web/pexels/tests/test_core.py::TestClientParsing::test_check_status_404 PASSED
cli_web/pexels/tests/test_core.py::TestClientParsing::test_check_status_429 PASSED
cli_web/pexels/tests/test_core.py::TestClientParsing::test_check_status_500 PASSED
cli_web/pexels/tests/test_core.py::TestNormalizers::test_normalize_photo PASSED
cli_web/pexels/tests/test_core.py::TestNormalizers::test_normalize_video_detail PASSED
cli_web/pexels/tests/test_core.py::TestNormalizers::test_normalize_user PASSED
cli_web/pexels/tests/test_core.py::TestNormalizers::test_normalize_collection PASSED
cli_web/pexels/tests/test_core.py::TestHelpers::test_sanitize_filename_removes_invalid_chars PASSED
cli_web/pexels/tests/test_core.py::TestHelpers::test_sanitize_filename_empty_string PASSED
cli_web/pexels/tests/test_core.py::TestHelpers::test_sanitize_filename_whitespace_only PASSED
cli_web/pexels/tests/test_core.py::TestHelpers::test_sanitize_filename_truncates PASSED
cli_web/pexels/tests/test_core.py::TestHelpers::test_handle_errors_catches_pexels_error PASSED
cli_web/pexels/tests/test_core.py::TestHelpers::test_handle_errors_catches_unknown_exception PASSED
cli_web/pexels/tests/test_core.py::TestHelpers::test_handle_errors_json_mode PASSED
cli_web/pexels/tests/test_core.py::TestOutput::test_print_json_valid PASSED
cli_web/pexels/tests/test_core.py::TestOutput::test_print_pagination_shows_info PASSED
cli_web/pexels/tests/test_core.py::TestOutput::test_print_pagination_empty PASSED
cli_web/pexels/tests/test_e2e.py::TestPexelsLive::test_search_photos PASSED
cli_web/pexels/tests/test_e2e.py::TestPexelsLive::test_search_photos_with_filters PASSED
cli_web/pexels/tests/test_e2e.py::TestPexelsLive::test_search_photos_pagination PASSED
cli_web/pexels/tests/test_e2e.py::TestPexelsLive::test_get_photo PASSED
cli_web/pexels/tests/test_e2e.py::TestPexelsLive::test_search_videos PASSED
cli_web/pexels/tests/test_e2e.py::TestPexelsLive::test_get_video PASSED
cli_web/pexels/tests/test_e2e.py::TestPexelsLive::test_get_user PASSED
cli_web/pexels/tests/test_e2e.py::TestPexelsLive::test_get_user_media PASSED
cli_web/pexels/tests/test_e2e.py::TestPexelsLive::test_get_collection PASSED
cli_web/pexels/tests/test_e2e.py::TestPexelsLive::test_discover PASSED
cli_web/pexels/tests/test_e2e.py::TestPexelsLive::test_search_suggestions PASSED
cli_web/pexels/tests/test_e2e.py::TestPexelsLive::test_not_found_raises PASSED
cli_web/pexels/tests/test_e2e.py::TestCLISubprocess::test_help PASSED
cli_web/pexels/tests/test_e2e.py::TestCLISubprocess::test_version PASSED
cli_web/pexels/tests/test_e2e.py::TestCLISubprocess::test_photos_search_json PASSED
cli_web/pexels/tests/test_e2e.py::TestCLISubprocess::test_photos_get_json PASSED
cli_web/pexels/tests/test_e2e.py::TestCLISubprocess::test_videos_search_json PASSED
cli_web/pexels/tests/test_e2e.py::TestCLISubprocess::test_users_get_json PASSED
cli_web/pexels/tests/test_e2e.py::TestCLISubprocess::test_collections_discover_json PASSED

49 passed in 9.72s
```
