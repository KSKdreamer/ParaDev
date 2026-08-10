# Build Diagnostics Bridge

## Summary

- Added `--strict-metadata` to the diagnostics CLI so the desktop Build page can ask the Python SDK for the same blocking metadata diagnostics as `Project.inspect("diagnostics")`.
- Added a Tauri `paradev_project_inspect` bridge and TypeScript `loadProjectInspection` helper for read-only project inspection payloads.
- Updated the Build page model to prefer fresh SDK diagnostics over cached browser diagnostics, including localized load failure copy.
- Kept PIHC3 unchanged for this slice; the real PIHC3 project is used as the desktop smoke target.

## Verification

- `rtk uv run pytest tests/test_cli.py -q -k diagnostics_cli_honors_strict_metadata`
- `rtk npm --prefix apps/desktop run test:unit -- src/buildPage/BuildPage.test.tsx src/buildPage/buildPageModel.test.ts src/services/paradev.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml`
- `rtk cargo fmt --manifest-path apps/desktop/src-tauri/Cargo.toml --check`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/cli.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run paradev diagnostics projects/PIHC3 --strict-metadata --json`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri`
- `rtk git diff --check`
