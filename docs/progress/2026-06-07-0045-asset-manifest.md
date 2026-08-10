# 2026-06-07 00:45 CST - Asset Manifest

## Done

- Added `.paradev/build/assets.json` as a first-class static-copy asset catalog.
- Derived asset rows from planned copy artifacts and the existing source index, including module id, family, slot, source path, artifact path, artifact owner, target root, hash/size metadata, optional image metadata, and resolved source metadata.
- Added a deterministic module/slot row index for editor, MCP, and GUI clients.
- Added low-level manifest coverage and a HOI4 project integration assertion for `assets/*` and `copy/*` slots.
- Updated workflow and architecture docs to list the new manifest contract.

## Verification

- Red first: `rtk bash scripts/test.bash tests/test_build_manifest.py -q` failed because `assets.json` was absent from `manifest_payloads`.
- Focused green: `rtk bash scripts/test.bash tests/test_build_manifest.py -q`
- Integration green: `rtk bash scripts/test.bash tests/test_build_manifest.py tests/test_project_build.py::test_hoi4_profile_preserves_static_copy_relative_paths -q`
- Owner field red/green: `rtk bash scripts/test.bash tests/test_build_manifest.py::test_manifest_payloads_include_copy_asset_catalog tests/test_project_build.py::test_hoi4_profile_preserves_static_copy_relative_paths -q`
- Related suite: `rtk bash scripts/test.bash tests/test_build_manifest.py tests/test_project_build.py tests/test_project.py tests/test_simple_source_family.py -q` passed 81 tests.
- Full suite: `rtk bash scripts/test.bash` passed 131 tests.
- CI lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/manifest.py tests/test_build_manifest.py tests/test_project_build.py`
- CLI smoke: `rtk uv run paradev build demos/assets/projects/minimal --emit-manifests --json`
- Emitted manifest check: `rtk uv run python -c 'import json; from pathlib import Path; payload = json.loads(Path("demos/assets/projects/minimal/.paradev/build/assets.json").read_text(encoding="utf-8")); assert payload["schema"] == "paradev.build.assets.v1"; assert payload["assets"] == []; assert payload["index"] == {}'`
- Whitespace check: `rtk git diff --check -- src/paradev/build/manifest.py tests/test_build_manifest.py tests/test_project_build.py docs/workflows/build-flow.md docs/goals/final-architecture.md docs/progress/2026-06-07-0045-asset-manifest.md`

## Linear

- `rtk command -v linear` still exits with status 1.
- Tool discovery for Linear issue management exposed Codex automation and GitHub tools only; no Linear connector is available in this session.

## Risks

- `assets.json` indexes planned copy artifacts; it does not yet include generated sprites or image conversion outputs because those compilers are not implemented.
- Existing unrelated desktop, README, and script changes remain intentionally untouched.

## Next

- Add an SDK/CLI asset inspection surface over `assets.json` so clients do not need to read manifest files directly.
- Verify HOI4 icon dimensions and texture format policy before attaching built-in family asset constraints.
