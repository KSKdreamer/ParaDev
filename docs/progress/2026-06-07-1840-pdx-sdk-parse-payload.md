# 2026-06-07 18:40 PDX SDK Parse Payload

## Scope

- Continued foundation work on `codex/scaffold-source-root-selection`.
- Focused on TAL-291 PDX parser stabilization and shared CLI/SDK inspection payloads.
- Moved the PDX parse payload contract into the Python SDK so CLI, scripts, GUI, MCP, and future editor surfaces have one reusable parse entrypoint.

## Changes

- Added `paradev.sdk.parse_pdx_file(...)` with the `paradev.pdx.parse.v1` payload contract.
- Exported `parse_pdx_file` and `PDX_PARSE_SCHEMA` from `paradev.sdk`.
- Changed `paradev parse` to delegate to the SDK helper instead of owning a duplicate parser payload implementation.
- Preserved CLI behavior: successful parses exit zero, invalid or unreadable files print diagnostics and exit non-zero.
- Preserved SDK behavior for automation: invalid or unreadable files return `ok: false` diagnostics instead of raising.
- Documented the SDK helper in the English and Chinese Python SDK manual and in the build-flow parser docs.

## Verification

- Red tests first:
  - `rtk uv run pytest tests/test_sdk_examples.py -k 'parse_pdx_file' tests/test_cli.py::test_parse_cli_matches_sdk_payload` failed before implementation because `paradev.sdk.parse_pdx_file` was not exported.
- Focused green:
  - `rtk uv run pytest tests/test_sdk_examples.py -k 'parse_pdx_file'`.
  - `rtk uv run pytest tests/test_cli.py::test_parse_cli_matches_sdk_payload tests/test_cli.py::test_parse_can_include_token_rows_json tests/test_cli.py::test_parse_outputs_diagnostics_json_for_invalid_pdx tests/test_cli.py::test_parse_outputs_diagnostics_json_for_missing_source`.
- SDK smoke:
  - `rtk uv run python` importing `parse_pdx_file` and parsing `demos/assets/projects/minimal/src/modules/focus/GER_sample/def.pdx` with `include_tokens=True`.
- CLI smoke:
  - `rtk uv run paradev parse demos/assets/projects/minimal/src/modules/focus/GER_sample/def.pdx --tokens --json`.
- Format:
  - `rtk uv run black src/paradev/cli.py src/paradev/sdk/pdx.py src/paradev/sdk/__init__.py tests/test_cli.py tests/test_sdk_examples.py`.
- Heaven-style scan:
  - `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/pdx.py src/paradev/sdk/__init__.py src/paradev/cli.py tests/test_sdk_examples.py tests/test_cli.py`.
- Whitespace review:
  - `rtk git diff --check`.
- Lint gate:
  - `rtk bash scripts/flake.bash --ci`.
- Test gate:
  - `rtk bash scripts/test.bash` (`350 passed`).
- Build gate:
  - `rtk uv build`.

## Review

- The CLI is now a thin surface over the SDK parse helper, which keeps the developer mental model smaller and prevents future GUI/MCP integrations from copying CLI-only logic.
- Token rows and lossless dumps remain opt-in, so HoI4 mod authors still get the compact parse projection by default.
- Error handling stays structured and JSON-safe across source-not-found, unreadable-source, and parser-diagnostic paths.
- No PIHC3 migration files were touched.

## Linear

- Attempted to read `TAL-295`; Linear MCP returned `UNAUTHORIZED` / `Session expired`.
- Attempted to read `TAL-291`; Linear MCP returned the same auth error.
- Linear updates could not be posted from this session until the app is re-authenticated.
