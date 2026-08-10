# Derived Collections Progress

Date: 2026-06-06 20:11 CST

Linear: TAL-293

## Done

- Added deterministic collection derivation from module `collection_id` when explicit collections are not supplied.
- Kept explicit SDK `collections=` authoritative for tests and custom callers.
- Applied derived collections before family artifact emission in `plan_build(...)`.
- Added project-level coverage for discovered `meta.yaml` collection metadata.
- Updated build-flow docs with the current collection derivation behavior.

## Verification

- `rtk uv run pytest tests/test_build_records.py tests/test_build_manifest.py tests/test_project_build.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/__init__.py src/paradev/build/records.py src/paradev/build/plan.py tests/test_build_records.py tests/test_build_manifest.py tests/test_project_build.py`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- Derived collection family currently uses the member module family; collection descriptor loading is still future work.
- Existing local desktop and README edits remain outside this build graph slice.

## Next

- Add collection descriptor loading or the first collection-aware focus family compiler.
