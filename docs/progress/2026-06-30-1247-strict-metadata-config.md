# Strict Metadata Config

Promoted strict metadata from a Build page local setting into the SDK-backed `paradev.build.strict_metadata` config path.

- Added `paradev.build.strict_metadata` to package defaults, desktop config allowlist/validation, generated desktop keys, and Config page Build defaults.
- Changed `Project.build`, `Project.diagnostics`, module discovery, collection discovery, REST build, CLI build/diagnostics, and desktop build command planning to treat omitted `strict_metadata` as `CM_PARADEV` inheritance while preserving explicit true/false overrides.
- Updated BuildPage to read/write strict metadata through the desktop config bridge and to remove the legacy `paradev.build.strictMetadata` localStorage key.
- Regenerated frontend, desktop, and project API references/contracts, then updated docs to describe inherited versus explicit strict metadata behavior.

Verification:

- `rtk uv run pytest tests/test_project.py::test_project_build_strict_metadata_blocks_unknown_module_keys tests/test_project.py::test_project_build_strict_metadata_uses_configured_default tests/test_desktop_api_selection.py::test_desktop_project_build_command_matches_tauri_build_flags tests/test_desktop_api_selection.py::test_desktop_project_build_command_uses_configured_strict_metadata tests/test_desktop_api_selection.py::test_desktop_config_value_round_trips_strict_metadata -q`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/config.py src/paradev/cli.py src/paradev/desktop/local.py src/paradev/desktop/shell.py src/paradev/sdk/frontend_api.py src/paradev/sdk/project.py src/paradev/surfaces/rest.py tests/test_architecture.py tests/test_cli.py tests/test_desktop_api_selection.py tests/test_native_web_bridge.py tests/test_project.py`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 5210` reached Vite ready, compiled `paradev-desktop`, launched `target/debug/paradev-desktop`, then was stopped with Ctrl-C.
