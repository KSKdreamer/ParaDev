# Artifact Module Provenance Progress

Date: 2026-06-07 10:31

Linear: TAL-293 (update attempted; Linear connector returned `UNAUTHORIZED; Session expired. Please re-authenticate.`)

## Done

- Extended artifact inspection so `--module` and `Project.artifacts(module_id=...)` return artifacts that involve a module, including collection-owned PDX output, build-root focus-tree view artifacts, and module-owned localization.
- Added `module` and `collection` buckets to the artifacts manifest index using owner prefixes plus metadata provenance such as `module_ids`, `collection_id`, and focus-tree view `nodes`.
- Updated CLI help and `docs/workflows/build-flow.md` to distinguish exact `--owner` filtering from source-involvement `--module` and `--collection` filtering.

## Verification

- Red first: focused manifest, SDK, and CLI artifact tests failed on missing `module`/`collection` provenance.
- `rtk bash scripts/test.bash tests/test_build_manifest.py::test_manifest_payloads_and_writes_include_source_map_and_summary tests/test_project.py::test_project_artifacts_returns_filtered_manifest_payload_without_writing tests/test_project.py::test_project_cli_filters_artifacts_manifest_json -q` -> 3 passed.
- `rtk bash scripts/test.bash tests/test_build_manifest.py tests/test_project.py tests/test_project_build.py tests/test_cli.py -q` -> 159 passed.
- `rtk bash scripts/flake.bash --ci` -> passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/manifest.py src/paradev/build/__init__.py src/paradev/sdk/project.py src/paradev/cli.py tests/test_build_manifest.py tests/test_project.py` -> passed.
- `rtk bash scripts/test.bash` -> 269 passed.

## Risks Or Blockers

- Linear OAuth is expired in this Codex session, so issue comments cannot be created until the app is re-authenticated.

## Next

- Continue toward the generic module compilation system by exposing the same provenance model through higher-level build explanations and future HeavenBase catalog rows.
