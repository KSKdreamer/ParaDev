# Diagnostic Family Index Progress

Date: 2026-06-07 10:07 CST

Linear: attempted to comment on `TAL-293`, but `_save_comment` returned `UNAUTHORIZED`; the session needs re-authentication before issue comments can be saved.

## Done

- Added an additive `family_index` to `diagnostics.json` payloads.
- Kept the existing severity/code `index` unchanged for compatibility.
- Recomputed `family_index` for filtered `Project.diagnostics(...)` and `paradev diagnostics` responses.
- Matched diagnostic family from either a direct row `family` field or resolved `source.family`.
- Updated diagnostics workflow docs and SDK/CLI manifest tests.

## Verification

- Red first: `rtk bash scripts/test.bash tests/test_build_manifest.py::test_manifest_payloads_and_writes_include_source_map_and_summary tests/test_project.py::test_project_diagnostics_returns_filtered_manifest_payload_without_writing tests/test_project.py::test_project_cli_filters_diagnostics_manifest_json -q` failed because `family_index` was missing.
- Focused green: the same command passed 3 tests after implementation.
- Related suite: `rtk bash scripts/test.bash tests/test_build_manifest.py tests/test_project.py tests/test_project_build.py -q` passed 148 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/manifest.py src/paradev/build/__init__.py src/paradev/sdk/project.py tests/test_build_manifest.py tests/test_project.py`
- Full suite: `rtk bash scripts/test.bash` passed 263 tests.

## Review

- The change is additive and avoids changing the existing `index` shape.
- The helper uses the same resolved source metadata as diagnostics filtering, so source-anchored diagnostics and row-anchored diagnostics behave consistently.
- GUI, MCP, and scripts can now pivot from family to severity/code without scanning every diagnostic row.

## Risks Or Blockers

- Linear issue sync remains blocked by expired connector authentication.

## Next

- Continue turning build manifests into low-friction inspection contracts for SDK, CLI, desktop, and MCP clients.
