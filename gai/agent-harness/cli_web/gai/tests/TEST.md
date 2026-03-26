# cli-web-gai — Test Plan & Results

## Test Inventory

| Suite | Class | Tests | Type |
|-------|-------|------:|------|
| test_core.py | TestExceptions | 3 | Unit |
| test_core.py | TestModels | 5 | Unit |
| test_core.py | TestHelpers | 6 | Unit |
| test_core.py | TestClientMocked | 8 | Unit (mocked Playwright) |
| test_e2e.py | TestLiveSearch | 1 | E2E (live browser) |
| test_e2e.py | TestCLISubprocess | 6 | Subprocess |
| **Total** | | **29** | |

## Unit Tests — test_core.py (23 tests)

### TestExceptions (3 tests)

| Test | What it verifies |
|------|-----------------|
| `test_all_exceptions_inherit_from_gai_error` | All 6 exception types inherit from GAIError |
| `test_timeout_error_has_timeout_seconds` | TimeoutError stores `timeout_seconds` attribute |
| `test_captcha_error_message` | CaptchaError preserves message string |

### TestModels (5 tests)

| Test | What it verifies |
|------|-----------------|
| `test_source_to_dict_minimal` | Source.to_dict() omits empty snippet |
| `test_source_to_dict_with_snippet` | Source.to_dict() includes snippet when present |
| `test_search_result_to_dict` | SearchResult.to_dict() full structure with sources + follow_up |
| `test_search_result_to_dict_no_followup` | SearchResult.to_dict() omits follow_up_prompt when empty |
| `test_search_result_to_dict_is_valid_json` | SearchResult.to_dict() is JSON-serializable |

### TestHelpers (6 tests)

| Test | What it verifies |
|------|-----------------|
| `test_json_error_format` | json_error() produces `{"error": true, "code": ..., "message": ...}` |
| `test_handle_errors_gai_error_exits_1` | GAIError triggers SystemExit(1) |
| `test_handle_errors_unexpected_exits_2` | Unhandled Exception triggers SystemExit(2) |
| `test_handle_errors_keyboard_interrupt_exits_130` | KeyboardInterrupt triggers SystemExit(130) |
| `test_handle_errors_captcha_exits_1` | CaptchaError triggers SystemExit(1) |
| `test_handle_errors_json_mode_outputs_json` | JSON mode wraps errors as structured JSON |
| `test_handle_errors_json_mode_captcha` | JSON mode maps CaptchaError to CAPTCHA_REQUIRED code |

### TestClientMocked (8 tests)

| Test | What it verifies |
|------|-----------------|
| `test_search_returns_search_result` | search() returns SearchResult with answer + sources |
| `test_search_raises_captcha_error` | CAPTCHA selector triggers CaptchaError |
| `test_search_raises_parse_error_on_null` | Null DOM extraction triggers ParseError |
| `test_search_network_error_on_goto_failure` | Navigation failure triggers NetworkError |
| `test_client_context_manager` | `with GAIClient()` calls close() on exit |
| `test_browser_launch_failure_raises_browser_error` | Chromium launch failure triggers BrowserError |
| `test_search_with_empty_sources` | Search with no sources returns empty list |
| `test_followup_without_prior_search_raises` | followup() without prior search raises BrowserError |

## E2E Tests — test_e2e.py (6 tests)

### TestLiveSearch (1 test)

| Test | What it verifies |
|------|-----------------|
| `test_search_returns_answer_with_structure` | Live query returns answer, valid JSON, source URLs (skips on CAPTCHA) |

### TestCLISubprocess (6 tests)

| Test | What it verifies |
|------|-----------------|
| `test_help_output` | `--help` displays usage info |
| `test_search_help` | `search --help` displays search subcommands |
| `test_version` | `--version` displays 0.1.0 |
| `test_search_ask_json` | `search ask --json` returns valid JSON with answer |
| `test_search_ask_plain` | `search ask` returns plain text answer |
| `test_search_ask_lang` | `search ask --lang en` respects language parameter |

## Running Tests

```bash
cd gai/agent-harness
pip install -e .

# All unit tests (fast, no network)
python -m pytest cli_web/gai/tests/test_core.py -v -s

# Subprocess tests (requires pip install)
CLI_WEB_FORCE_INSTALLED=1 python -m pytest cli_web/gai/tests/test_e2e.py::TestCLISubprocess -v -s

# Live E2E tests (launches browser, may hit CAPTCHA)
python -m pytest cli_web/gai/tests/test_e2e.py::TestLiveSearch -v -s

# Everything
python -m pytest cli_web/gai/tests/ -v -s
```

## Test Results

**Run date:** 2026-03-25
**Environment:** Python 3.12.8, Windows 11, pytest 8.3.4

### Unit tests (test_core.py)

```
23 passed in 0.32s
```

| Class | Result |
|-------|--------|
| TestExceptions (3) | 3 passed |
| TestModels (5) | 5 passed |
| TestHelpers (6) | 6 passed |
| TestClientMocked (8) | 8 passed |
