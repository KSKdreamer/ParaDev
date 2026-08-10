# Collection Inspection Progress

Date: 2026-06-07 10:13 CST

Linear: attempted to comment on `TAL-293`, but `_save_comment` returned `UNAUTHORIZED`; the session needs re-authentication before issue comments can be saved.

## Done

- Added a deterministic collection manifest `index` keyed by collection id, family, and member module id.
- Added `Project.collections(...)` for filtered collection inspection without writing build outputs.
- Added `paradev collections` with `--family`, `--collection`, and `--module` filters.
- Updated build-flow docs with the new collection inspection path.

## Verification

- Red first: `rtk bash scripts/test.bash tests/test_build_manifest.py::test_manifest_payloads_and_writes_include_source_map_and_summary tests/test_project.py::test_project_collections_returns_filtered_manifest_payload_without_writing tests/test_project.py::test_project_cli_filters_collections_manifest_json -q` failed because `collections.json` had no `index`, `Project.collections(...)` did not exist, and `paradev collections` was not registered.
- Focused green: the same command passed 3 tests after implementation.
- Related suite: `rtk bash scripts/test.bash tests/test_build_manifest.py tests/test_project.py tests/test_project_build.py tests/test_cli.py -q` passed 157 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/cli.py src/paradev/sdk/project.py src/paradev/build/manifest.py src/paradev/build/__init__.py tests/test_build_manifest.py tests/test_project.py`
- Full suite: `rtk bash scripts/test.bash` passed 267 tests.

## Review

- The change mirrors module inspection and keeps the public mental model centered on project, module, collection, artifact, and family.
- Filtering recomputes the index over returned rows, matching the other manifest inspection APIs.
- The command stays read-only and uses a fresh dry build plan.

## Risks Or Blockers

- Linear issue sync remains blocked by expired connector authentication.

## Next

- Continue exposing the core project/module/collection/artifact model through read-only SDK and CLI views.
