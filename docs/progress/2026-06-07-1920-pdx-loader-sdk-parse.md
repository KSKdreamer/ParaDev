# 2026-06-07 19:20 PDX Loader SDK Parse Payload

## Scope

- Continued foundation work on `codex/scaffold-source-root-selection`.
- Focused on general SDK/build modularity, not PIHC3 migration or GUI work.
- Stabilized the generic PDX source loader so project builds share the SDK parse payload used by CLI, REST, MCP, GUI, and scripts.

## Changes

- Updated `load_pdx_sources(...)` to call `parse_pdx_file(..., include_dump=True)` and reconstruct `PDXBlock` sources from the lossless dump payload.
- Added build diagnostic mapping for SDK parser rows, preserving existing `pdx.missing_source`, `pdx.unreadable_source`, and parser diagnostic codes while adding module, collection, slot, and relative source-path context.
- Tightened `parse_pdx_file(...)` unreadable-source payloads so plain `OSError("permission denied")` still reports the useful reason when `strerror` is absent.
- Documented the shared parser payload in `docs/workflows/build-flow.md`.
- Updated the English and Chinese developer manual guidance so family compilers and adapters use `load_pdx_sources(...)` or `parse_pdx_file(..., include_dump=True)` instead of direct surface-owned `PDXBlock.from_file(...)` reads.

## Verification

- Red tests first:
  - `rtk uv run pytest tests/test_build_loaders.py::test_pdx_loader_uses_sdk_parse_payload tests/test_build_loaders.py::test_pdx_loader_maps_sdk_parse_payload_diagnostics` failed because `paradev.build.loaders` did not expose or call `parse_pdx_file`.
- Focused green:
  - `rtk uv run pytest tests/test_build_loaders.py::test_pdx_loader_uses_sdk_parse_payload tests/test_build_loaders.py::test_pdx_loader_maps_sdk_parse_payload_diagnostics tests/test_build_loaders.py::test_pdx_loader_reports_unreadable_source_as_diagnostic`.
  - `rtk uv run pytest tests/test_build_loaders.py` (`19 passed`).
  - `rtk uv run pytest tests/test_build_loaders.py tests/test_sdk_examples.py -k 'parse_pdx_file or pdx_loader'` (`12 passed, 13 deselected`).
- Import smoke:
  - `rtk uv run python -c 'from paradev.build import load_pdx_sources; from paradev.sdk import parse_pdx_file; print(load_pdx_sources.__name__, parse_pdx_file.__name__)'`.
- Format:
  - `rtk uv run black src/paradev/build/loaders.py src/paradev/sdk/pdx.py tests/test_build_loaders.py`.
- Heaven-style scan:
  - `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/loaders.py src/paradev/sdk/pdx.py tests/test_build_loaders.py`.
- Whitespace review:
  - `rtk git diff --check`.
- Lint gate:
  - `rtk bash scripts/flake.bash --ci`.
- Test gate:
  - `rtk bash scripts/test.bash` (`361 passed`).
- Build gate:
  - `rtk uv build`.

## Review

- Build graph PDX parsing no longer owns a separate direct file-read/parser exception path, so future editor, importer, MCP, REST, and CLI surfaces can reason about one parse payload.
- The build loader still returns build-owned `Diagnostic` records, so module and collection context remains attached at the compiler boundary.
- The SDK unreadable-source fallback is a compatibility improvement for all callers and preserves existing build diagnostic wording.
- No PIHC3 migration files or GUI files were touched.

## Linear

- Attempted to read `TAL-295`; Linear MCP returned `UNAUTHORIZED` / `Session expired`.
- Linear updates could not be posted from this session until the app is re-authenticated.
