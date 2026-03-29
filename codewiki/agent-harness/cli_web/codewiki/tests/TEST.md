# TEST.md — cli-web-codewiki

## Part 1: Test Plan

### Test Inventory

| File | Tests | Layer |
|------|-------|-------|
| `test_core.py` | 56 | Unit (mocked HTTP) |
| `test_e2e.py` | 26 | E2E live + subprocess |
| **Total** | **82** | |

### Unit Tests (`test_core.py`)

**RPC Encoder (5 tests):** URL construction with rpcids param, f.req encoding for empty and parameterized requests, form-encoded output.

**RPC Decoder (8 tests):** XSSI prefix stripping (string + bytes), featured/search/chat response parsing, None for empty results, RPCError on error entries, wrong rpc_id returns None.

**Client — Featured Repos (2 tests):** Parse realistic batchexecute response into Repository objects, empty response returns empty list.

**Client — Search Repos (2 tests):** Parse search results with correct fields, query params passed correctly.

**Client — Wiki Page (2 tests):** Parse sections with levels/titles/content, NotFoundError on null response.

**Client — Chat (2 tests):** Parse chat answer string, conversation history support.

**Client — HTTP Errors (7 tests):** 404→NotFoundError, 429→RateLimitError (with and without Retry-After), 500/503→ServerError, ConnectError→NetworkError, TimeoutException→NetworkError.

**Exception Hierarchy (12 tests):** All exceptions inherit CodeWikiError, error_code_for() mapping for all 6 types + unknown, AuthError.recoverable, RateLimitError.retry_after, ServerError.status_code, RPCError.code.

**Handle Errors (7 tests):** CodeWikiError exits 1, unexpected Exception exits 2, KeyboardInterrupt exits 130, successful yield, UsageError propagates, JSON output format for both error types.

**Models (5 tests):** Repository.org/name properties, to_dict() keys, WikiSection/WikiPage/ChatResponse serialization, section_count in WikiPage.

**RPC Types (2 tests):** Method ID constants exist, batchexecute URL is HTTPS.

### E2E Tests (`test_e2e.py`)

**Live Repos (5 tests):** Featured repos returns data with slug/stars, search for "react" finds results, nonsense search returns empty list, limit parameter works, slug format is org/name.

**Live Wiki (5 tests):** Wiki get returns sections with commit hash, first section has content >50 chars, nonexistent repo raises NotFoundError, all sections have typed fields, github_url is correct.

**Live Chat (3 tests):** Chat returns answer >50 chars, no RPC data leaks (wrb.fr, af.httprm), answer is a string.

**CLI Subprocess (12 tests):** --help loads with all commands, repos/wiki/chat help, repos featured/search --json, wiki sections/get --json, chat ask --json, 404 error returns JSON error shape, plain text table output exits 0.

**Read-Only Round Trip (2 tests):** Search slug matches wiki page slug, featured repo can have wiki fetched.

### No-Auth Notes

Code Wiki is fully public — no auth module, no auth tests. All tests run without credentials.

---

## Part 2: Test Results

**Date:** 2026-03-29
**Pass Rate:** 82/82 (100%)

### Unit Tests (`test_core.py`)

```
test_core.py::TestRPCEncoder::test_build_url_contains_rpcid PASSED
test_core.py::TestRPCEncoder::test_build_url_contains_base PASSED
test_core.py::TestRPCEncoder::test_encode_request_featured_empty_params PASSED
test_core.py::TestRPCEncoder::test_encode_request_search_with_query_params PASSED
test_core.py::TestRPCEncoder::test_encode_request_produces_form_encoded PASSED
test_core.py::TestRPCDecoder::test_strip_prefix_removes_xssi PASSED
test_core.py::TestRPCDecoder::test_strip_prefix_handles_bytes PASSED
test_core.py::TestRPCDecoder::test_strip_prefix_no_prefix_unchanged PASSED
test_core.py::TestRPCDecoder::test_decode_featured_response PASSED
test_core.py::TestRPCDecoder::test_decode_returns_none_for_empty PASSED
test_core.py::TestRPCDecoder::test_decode_rpc_error_raises PASSED
test_core.py::TestRPCDecoder::test_decode_search_response PASSED
test_core.py::TestRPCDecoder::test_decode_chat_response PASSED
test_core.py::TestRPCDecoder::test_decode_wrong_rpc_id_returns_none PASSED
test_core.py::TestCodeWikiClientFeaturedRepos::test_featured_repos_parses_correctly PASSED
test_core.py::TestCodeWikiClientFeaturedRepos::test_featured_repos_empty_returns_list PASSED
test_core.py::TestCodeWikiClientSearchRepos::test_search_repos_parses_correctly PASSED
test_core.py::TestCodeWikiClientSearchRepos::test_search_repos_passes_query_to_rpc PASSED
test_core.py::TestCodeWikiClientWikiPage::test_wiki_page_parses_sections PASSED
test_core.py::TestCodeWikiClientWikiPage::test_wiki_page_not_found_raises PASSED
test_core.py::TestCodeWikiClientChat::test_chat_returns_answer PASSED
test_core.py::TestCodeWikiClientChat::test_chat_with_history PASSED
test_core.py::TestClientHTTPErrors::test_client_404_raises_not_found PASSED
test_core.py::TestClientHTTPErrors::test_client_429_raises_rate_limit PASSED
test_core.py::TestClientHTTPErrors::test_client_429_no_retry_after_header PASSED
test_core.py::TestClientHTTPErrors::test_client_500_raises_server_error PASSED
test_core.py::TestClientHTTPErrors::test_client_503_raises_server_error PASSED
test_core.py::TestClientHTTPErrors::test_client_network_error_connect PASSED
test_core.py::TestClientHTTPErrors::test_client_network_error_timeout PASSED
test_core.py::TestExceptionHierarchy::test_all_errors_are_codewiki_errors PASSED
test_core.py::TestExceptionHierarchy::test_error_code_mapping_auth PASSED
test_core.py::TestExceptionHierarchy::test_error_code_mapping_rate_limit PASSED
test_core.py::TestExceptionHierarchy::test_error_code_mapping_not_found PASSED
test_core.py::TestExceptionHierarchy::test_error_code_mapping_server_error PASSED
test_core.py::TestExceptionHierarchy::test_error_code_mapping_network PASSED
test_core.py::TestExceptionHierarchy::test_error_code_mapping_rpc PASSED
test_core.py::TestExceptionHierarchy::test_error_code_mapping_unknown PASSED
test_core.py::TestExceptionHierarchy::test_auth_error_recoverable_default_true PASSED
test_core.py::TestExceptionHierarchy::test_auth_error_recoverable_can_be_false PASSED
test_core.py::TestExceptionHierarchy::test_rate_limit_error_stores_retry_after PASSED
test_core.py::TestExceptionHierarchy::test_server_error_stores_status_code PASSED
test_core.py::TestExceptionHierarchy::test_rpc_error_stores_code PASSED
test_core.py::TestHandleErrors::test_handle_errors_codewiki_error_exits_1 PASSED
test_core.py::TestHandleErrors::test_handle_errors_codewiki_error_json_output PASSED
test_core.py::TestHandleErrors::test_handle_errors_unexpected_exits_2 PASSED
test_core.py::TestHandleErrors::test_handle_errors_unexpected_json_output PASSED
test_core.py::TestHandleErrors::test_handle_errors_keyboard_interrupt_exits_130 PASSED
test_core.py::TestHandleErrors::test_handle_errors_no_error_yields PASSED
test_core.py::TestHandleErrors::test_handle_errors_usage_error_propagates PASSED
test_core.py::TestModels::test_repository_org_and_name_properties PASSED
test_core.py::TestModels::test_repository_to_dict_keys PASSED
test_core.py::TestModels::test_wiki_section_to_dict PASSED
test_core.py::TestModels::test_wiki_page_to_dict_includes_section_count PASSED
test_core.py::TestModels::test_chat_response_to_dict PASSED
test_core.py::TestRPCTypes::test_rpc_method_ids PASSED
test_core.py::TestRPCTypes::test_batchexecute_url_is_https PASSED

56 passed in 4.72s
```

### E2E Tests (`test_e2e.py`)

```
test_e2e.py::TestLiveRepos::test_featured_repos_returns_data PASSED
test_e2e.py::TestLiveRepos::test_search_returns_results PASSED
test_e2e.py::TestLiveRepos::test_search_empty_query_returns_empty PASSED
test_e2e.py::TestLiveRepos::test_search_with_limit PASSED
test_e2e.py::TestLiveRepos::test_featured_repo_slugs_have_org_and_name PASSED
test_e2e.py::TestLiveWiki::test_wiki_get_returns_sections PASSED
test_e2e.py::TestLiveWiki::test_wiki_sections_have_content PASSED
test_e2e.py::TestLiveWiki::test_wiki_not_found PASSED
test_e2e.py::TestLiveWiki::test_wiki_sections_structure PASSED
test_e2e.py::TestLiveWiki::test_wiki_repo_metadata PASSED
test_e2e.py::TestLiveChat::test_chat_returns_answer PASSED
test_e2e.py::TestLiveChat::test_chat_no_rpc_leak PASSED
test_e2e.py::TestLiveChat::test_chat_answer_is_string PASSED
test_e2e.py::TestCLISubprocess::test_help_loads PASSED
test_e2e.py::TestCLISubprocess::test_repos_help PASSED
test_e2e.py::TestCLISubprocess::test_wiki_help PASSED
test_e2e.py::TestCLISubprocess::test_repos_featured_json PASSED
test_e2e.py::TestCLISubprocess::test_repos_search_json PASSED
test_e2e.py::TestCLISubprocess::test_repos_search_limit PASSED
test_e2e.py::TestCLISubprocess::test_wiki_sections_json PASSED
test_e2e.py::TestCLISubprocess::test_wiki_get_json PASSED
test_e2e.py::TestCLISubprocess::test_chat_ask_json PASSED
test_e2e.py::TestCLISubprocess::test_wiki_not_found_returns_error_json PASSED
test_e2e.py::TestCLISubprocess::test_repos_featured_no_json_exits_zero PASSED
test_e2e.py::TestReadOnlyRoundTrip::test_list_detail_consistency PASSED
test_e2e.py::TestReadOnlyRoundTrip::test_featured_to_wiki_round_trip PASSED

26 passed in 61.62s
```

### Summary

| Suite | Passed | Failed | Total | Time |
|-------|--------|--------|-------|------|
| Unit (test_core.py) | 56 | 0 | 56 | 4.72s |
| E2E (test_e2e.py) | 26 | 0 | 26 | 61.62s |
| **Total** | **82** | **0** | **82** | **66.34s** |
