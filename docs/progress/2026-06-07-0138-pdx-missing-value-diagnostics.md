# 2026-06-07 01:38 CST - PDX Missing Value Diagnostics

## Done

- Added structured parser diagnostics for PDX operators with no following value.
- Threaded the new `pdx.missing_value` parser failure through the generic PDX source loader as a build diagnostic with module id, slot, source path, and span.
- Updated the build-flow guide so users know malformed PDX syntax is surfaced before artifact planning for that source.

## Verification

- Red first: `rtk bash scripts/test.bash tests/test_pdx_roundtrip.py::test_parser_reports_structured_diagnostics_for_missing_operator_values tests/test_build_loaders.py::test_pdx_loader_reports_missing_operator_value_diagnostics -q` failed because `focus =` parsed as a source instead of raising `PDXParseError`.
- Focused green: `rtk bash scripts/test.bash tests/test_pdx_roundtrip.py::test_parser_reports_structured_diagnostics_for_missing_operator_values tests/test_build_loaders.py::test_pdx_loader_reports_missing_operator_value_diagnostics -q`
- Related suite: `rtk bash scripts/test.bash tests/test_pdx_roundtrip.py tests/test_pdx_token.py tests/test_build_loaders.py -q` passed 18 tests.
- Full suite: `rtk bash scripts/test.bash` passed 144 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/pdx/parser.py tests/test_pdx_roundtrip.py tests/test_build_loaders.py`
- Parser smoke: `rtk uv run python -c "from paradev.pdx import PDXBlock, PDXParseError ..."`
- Whitespace: `rtk git diff --check -- src/paradev/pdx/parser.py tests/test_pdx_roundtrip.py tests/test_build_loaders.py docs/workflows/build-flow.md docs/progress/2026-06-07-0138-pdx-missing-value-diagnostics.md`

## Linear

- `rtk command -v linear` exits with status 1.
- Tool discovery for Linear issue management exposed Codex automation and GitHub tools only; no Linear connector is available in this session.

## Risks

- This slice only validates missing values after operators. Unterminated strings and other lexical errors remain parser-hardening follow-ups.
- Existing unrelated desktop, README, and script changes remain intentionally untouched.

## Next

- Continue hardening the PDX core where malformed source can otherwise masquerade as valid AST state.
- Add lexical diagnostics for unterminated strings or unsupported token sequences when fixtures expose the next parser failure mode.
