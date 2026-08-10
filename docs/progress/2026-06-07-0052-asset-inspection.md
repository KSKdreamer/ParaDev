# 2026-06-07 00:52 CST - Asset Inspection

## Done

- Added public `asset_index(...)` for deterministic module/slot asset lookup payloads.
- Added `Project.assets(...)` to return the current asset manifest without writing build files.
- Added `paradev assets` with `--family`, `--module`, `--slot`, and `--format` filters.
- Added SDK and CLI tests using a real PNG header so image metadata filtering is covered.
- Updated build-flow docs with the asset inspection command and SDK example.

## Verification

- Red first: `rtk bash scripts/test.bash tests/test_project.py::test_project_assets_returns_filtered_manifest_payload_without_writing tests/test_project.py::test_project_cli_filters_asset_manifest_json -q` failed because `Project.assets` and the `assets` command did not exist.
- Focused green: `rtk bash scripts/test.bash tests/test_project.py::test_project_assets_returns_filtered_manifest_payload_without_writing tests/test_project.py::test_project_cli_filters_asset_manifest_json -q`
- Related suite: `rtk bash scripts/test.bash tests/test_project.py tests/test_build_manifest.py tests/test_project_build.py -q` passed 69 tests.
- Full suite: `rtk bash scripts/test.bash` passed 133 tests.
- CI lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/manifest.py src/paradev/build/__init__.py src/paradev/sdk/project.py src/paradev/cli.py tests/test_project.py`
- CLI smoke: `rtk uv run paradev assets demos/assets/projects/minimal --json`
- Whitespace check: `rtk git diff --check -- src/paradev/build/manifest.py src/paradev/build/__init__.py src/paradev/sdk/project.py src/paradev/cli.py tests/test_project.py docs/workflows/build-flow.md docs/progress/2026-06-07-0052-asset-inspection.md`

## Linear

- `rtk command -v linear` still exits with status 1.
- Tool discovery for Linear issue management exposed Codex automation and GitHub tools only; no Linear connector is available in this session.

## Risks

- Asset inspection covers planned static copy assets only; generated sprites and image conversion outputs remain future compiler work.
- Existing unrelated desktop, README, and script changes remain intentionally untouched.

## Next

- Use this asset inspection surface from desktop/MCP payloads once those clients consume live SDK data.
- Verify HOI4 icon dimensions and texture format policy before attaching built-in family asset constraints.
