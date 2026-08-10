# Localization Manifest Progress

Date: 2026-06-06 21:39 CST

Linear: TAL-294

## Done

- Added `.paradev/build/localization.json` as a build manifest with schema `paradev.build.localization.v1`.
- Projected loaded localization rows with module id, family, canonical language, key, text, source path, resolved source metadata, and module-local duplicate state.
- Covered synthetic build results with duplicate localization rows and the demo project `--emit-manifests` path.
- Updated the build-flow workflow and final architecture manifest list.

## Verification

- `rtk bash scripts/test.bash tests/test_build_manifest.py tests/test_project.py tests/test_sdk_examples.py tests/test_localization_loader.py tests/test_project_build.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/manifest.py tests/test_build_manifest.py tests/test_project.py`
- `rtk uv run paradev build demos/assets/projects/minimal --emit-manifests --json`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- Duplicate state is intentionally module-local in this manifest; global localization collision policy should wait for a project-level localization index.
- Existing local desktop and README edits remain outside this manifest slice.

## Next

- Add a compact CLI or SDK helper to inspect build-root localization rows without requiring users or surfaces to know the manifest file layout.
