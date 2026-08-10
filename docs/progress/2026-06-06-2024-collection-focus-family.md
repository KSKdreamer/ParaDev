# Collection Focus Family Progress

Date: 2026-06-06 20:24 CST

Linear: TAL-293

## Done

- Added `CollectionPDXFamily` for collection-owned PDX artifacts from member modules.
- Kept the beginner fallback path for focus modules without collection metadata.
- Updated the HOI4 profile so focus PDX is collection-owned when `collection` is declared, while localization and copy artifacts stay module-owned.
- Updated the minimal demo project to put `GER_sample` in `GER_main`.
- Updated SDK, CLI, source-map, artifact emission, and workflow docs for `common/national_focus/GER_main.txt`.

## Verification

- `rtk uv run pytest tests/test_simple_source_family.py tests/test_project.py tests/test_project_build.py tests/test_sdk_examples.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/__init__.py src/paradev/build/families.py src/paradev/games/hoi4/__init__.py tests/test_simple_source_family.py tests/test_project.py tests/test_project_build.py tests/test_sdk_examples.py`
- `rtk uv run paradev build demos/assets/projects/minimal --json`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- The collection compiler concatenates PDX entries; focus-tree semantic validation and layout handling are still future slices.
- Existing local desktop and README edits remain outside this collection compiler slice.

## Next

- Add collection-level validation for duplicate focus IDs and missing project-local prerequisites.
