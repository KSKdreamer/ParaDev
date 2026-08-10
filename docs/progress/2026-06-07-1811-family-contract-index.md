# 2026-06-07 18:11 Family Contract Index

## Scope

- Continued TAL-295 SDK/CLI stabilization on `codex/scaffold-source-root-selection`.
- Focused on generality and modularity for GUI, MCP, importer, and script clients rather than PIHC3 migration work.
- Added a deterministic lookup index to the `paradev.build.families.v1` capability payload.

## Changes

- `BuildRegistry.to_view()` now returns a derived `index` alongside `families` and `writers`.
- The index maps family id, compiler kind, module source slot, collection descriptor source slot, sprite slot, routed route id, and artifact writer type to returned row numbers.
- `Project.families()` and `paradev families --json` inherit the index without adding a separate SDK or CLI concept.
- English and Chinese user/developer manual pages now mention the index for HoI4 modders and integration developers.
- The build-flow workflow docs now describe the `families` index as part of the profile-owned capability contract.

## Verification

- Red test first: `rtk uv run pytest tests/test_project.py -k 'families_returns_profile_family_contracts or cli_outputs_profile_family_contracts'` failed with `KeyError: 'index'`.
- Focused green: `rtk uv run pytest tests/test_project.py -k 'families_returns_profile_family_contracts or cli_outputs_profile_family_contracts'`.
- CLI smoke: `rtk uv run paradev families demos/assets/projects/minimal --json`.
- Format: `rtk uv run black src/paradev/build/registry.py tests/test_project.py`.
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/registry.py tests/test_project.py`.
- Whitespace review: `rtk git diff --check`.
- Lint gate: `rtk bash scripts/flake.bash --ci`.
- Test gate: `rtk bash scripts/test.bash` (`343 passed`).
- Build gate: `rtk uv build`.

## Review

- The index is derived from the public rows and does not introduce a second source of truth.
- Empty index buckets are omitted, matching the existing manifest index pattern.
- The row-number contract keeps clients fast while preserving the existing `families` and `writers` list payloads for compatibility.
- No PIHC3 migration files were touched.

## Linear

- Attempted to read `TAL-295`; Linear MCP returned `UNAUTHORIZED` / `Session expired`.
- Attempted to post a progress comment to `TAL-295`; Linear MCP returned the same auth error.
