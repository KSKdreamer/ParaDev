# Artifact Inspection Progress

Date: 2026-06-07 10:20 CST

Linear: attempted to comment on `TAL-293`, but `_save_comment` returned `UNAUTHORIZED`; the session needs re-authentication before issue comments can be saved.

## Done

- Added a deterministic artifact manifest `index` keyed by artifact path, type, owner, target root, and mode.
- Added `Project.artifacts(...)` for filtered artifact inspection without writing build outputs.
- Added `paradev artifacts` with `--type`, `--target-root`, `--owner`, `--path`, `--mode`, `--module`, and `--collection` filters.
- Updated build-flow docs with the new artifact inspection path.

## Verification

- Red first: `rtk bash scripts/test.bash tests/test_build_manifest.py::test_manifest_payloads_and_writes_include_source_map_and_summary tests/test_project.py::test_project_artifacts_returns_filtered_manifest_payload_without_writing tests/test_project.py::test_project_cli_filters_artifacts_manifest_json -q` failed because `artifacts.json` had no `index`, `Project.artifacts(...)` did not exist, and `paradev artifacts` was not registered.
- Focused green: the same command passed 3 tests after implementation.
- Related suite: `rtk bash scripts/test.bash tests/test_build_manifest.py tests/test_project.py tests/test_project_build.py tests/test_cli.py -q` passed 159 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/cli.py src/paradev/sdk/project.py src/paradev/build/manifest.py src/paradev/build/__init__.py tests/test_build_manifest.py tests/test_project.py`
- Full suite: `rtk bash scripts/test.bash` passed 269 tests.

## Review

- The change completes the read-only surface for the core beginner concepts: modules, collections, artifacts, and families.
- Filtering recomputes the index over returned rows, matching the other manifest inspection APIs.
- The command stays read-only and uses a fresh dry build plan.

## Risks Or Blockers

- Linear issue sync remains blocked by expired connector authentication.

## Next

- Continue exposing the core project/module/collection/artifact model through read-only SDK and CLI views.
