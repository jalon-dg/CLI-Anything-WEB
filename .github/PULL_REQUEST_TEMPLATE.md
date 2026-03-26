## Description

<!-- Briefly describe the changes in this PR. -->

Fixes #<!-- issue number -->

## Type of Change

<!-- Check the one that applies: -->

- [ ] **New Web CLI** -- adds a CLI harness for a new website
- [ ] **New Feature** -- adds new functionality to an existing CLI or the plugin
- [ ] **Bug Fix** -- fixes incorrect behavior
- [ ] **Documentation** -- updates docs only
- [ ] **Other** -- please describe:

---

### For New Web CLIs

<!-- If this PR adds a new CLI, ALL items below must be checked. -->

- [ ] `<APP>.md` API map exists at `<app>/agent-harness/<APP>.md`
- [ ] `SKILL.md` exists in both `.claude/skills/<app>-cli/SKILL.md` and `cli_web/<app>/skills/SKILL.md`
- [ ] Unit tests at `cli_web/<app>/tests/test_core.py` are present and pass
- [ ] E2E tests at `cli_web/<app>/tests/test_e2e.py` are present
- [ ] `TEST.md` contains both Part 1 (plan) and Part 2 (results)
- [ ] `README.md` (repo root) includes the new CLI in the examples table
- [ ] `CLAUDE.md` Generated CLIs table includes the new CLI
- [ ] `registry.json` includes an entry for the new CLI
- [ ] `setup.py` uses `find_namespace_packages(include=["cli_web.*"])`
- [ ] `cli_web/` has NO `__init__.py` (namespace package)
- [ ] Every command supports `--json`
- [ ] `repl_skin.py` in `utils/` is an unmodified copy from the plugin

### For Existing CLI Modifications

<!-- If this PR modifies an existing CLI, ALL items below must be checked. -->

- [ ] All unit tests pass: `python -m pytest cli_web/<app>/tests/test_core.py -v`
- [ ] All E2E tests pass: `python -m pytest cli_web/<app>/tests/test_e2e.py -v`
- [ ] No test regressions -- no previously passing tests were removed or weakened
- [ ] `registry.json` entry is updated if commands changed
- [ ] REPL `_print_repl_help()` reflects any new commands or options

### General Checklist

- [ ] Code follows existing patterns and conventions
- [ ] `--json` flag is supported on any new commands
- [ ] Commit messages follow conventional format (`feat:`, `fix:`, `docs:`, `test:`)
- [ ] I have tested my changes locally

## Test Results

<!-- Paste the output of `pytest -v` for the affected CLI(s). -->

```
<paste test output here>
```
