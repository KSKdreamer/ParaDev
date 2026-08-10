# 2026-06-07 18:22 Family Contract Filters

## Scope

- Continued TAL-295 SDK/CLI stabilization on `codex/scaffold-source-root-selection`.
- Focused on the shared SDK contract for GUI, MCP, importer, and PIHC3-adjacent clients.
- Added exact filters for the `paradev.build.families.v1` payload so clients can inspect one contract without scanning the full profile payload.

## Changes

- `BuildRegistry.to_view(...)` now accepts exact filters for family id, compiler kind, module source slot, collection descriptor source slot, sprite slot, routed route id, and artifact writer type.
- `Project.families(...)` exposes the same filter vocabulary: `family`, `kind`, `source_slot`, `collection_source_slot`, `sprite_slot`, `route`, and `artifact_type`.
- `paradev families` exposes matching CLI flags.
- Filtered payloads rebuild `index` against the returned `families` and `writers` rows, keeping row lookup deterministic and local to the payload.
- English and Chinese user/developer docs now show filtered family inspection from the CLI and Python SDK.

## Verification

- Red tests first:
  - `rtk uv run pytest tests/test_project.py -k 'families_filters_profile_family_contracts or cli_filters_profile_family_contracts'` failed with missing SDK keyword and missing CLI option errors.
- Focused green:
  - `rtk uv run pytest tests/test_project.py -k 'families_filters_profile_family_contracts or cli_filters_profile_family_contracts'`.
  - `rtk uv run pytest tests/test_project.py -k 'families_returns_profile_family_contracts or families_filters_profile_family_contracts or cli_outputs_profile_family_contracts or cli_filters_profile_family_contracts'`.
- CLI smoke:
  - `rtk uv run paradev families demos/assets/projects/minimal --family idea --source-slot icon --artifact-type sprite_gfx --json`.
- Format:
  - `rtk uv run black src/paradev/build/registry.py src/paradev/sdk/project.py src/paradev/cli.py tests/test_project.py`.
- Heaven-style scan:
  - `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/registry.py src/paradev/sdk/project.py src/paradev/cli.py tests/test_project.py`.
- Whitespace review:
  - `rtk git diff --check`.
- Lint gate:
  - `rtk bash scripts/flake.bash --ci`.
- Test gate:
  - `rtk bash scripts/test.bash` (`345 passed`).
- Build gate:
  - `rtk uv build`.

## Review

- The filter logic is registry-owned, so SDK and CLI consumers share one payload implementation.
- Filters are exact-match only and do not add a query language.
- Family filters and writer filters are independent; `artifact_type` limits `writers`, while family/slot/route filters limit `families`.
- The index remains derived from returned rows and does not become a second source of truth.
- No PIHC3 migration files were touched.

## Linear

- Attempted to read `TAL-295`; Linear MCP returned `UNAUTHORIZED` / `Session expired`.
- Attempted to post a progress comment to `TAL-295`; Linear MCP returned the same auth error.
