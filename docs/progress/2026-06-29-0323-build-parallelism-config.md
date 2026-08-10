# Build Parallelism Config Page

Time: 2026-06-29 03:23 CST

Continued the GUI usability/API-alignment loop by exposing `CM_PARADEV["paradev.build.parallelism"]` as a real SDK-owned desktop config value instead of a GUI-only preference.

- Added `desktop_read_config_value(...)` and `desktop_write_config_value(...)` to the `paradev.desktop` facade, with an allowlisted `paradev.build.parallelism` key and JSON-safe payload schema.
- Wired Tauri commands, native-web REST endpoints, and TypeScript service helpers so the GUI reads/writes the same `CM_PARADEV` value used by Python and CLI behavior.
- Added the Config page Build defaults panel with translated English/Chinese labels and the visible `paradev.build.parallelism` key.
- Fixed native-web config bridge issues found during validation: `/desktop/app-config` now returns JSON-safe app settings, and loopback CORS preflight works for browser PUT calls.
- Regenerated the desktop API and API catalog references after the public desktop facade grew from 28 to 30 rows.

Validation:

- `PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 rtk bash scripts/run.bash --tauri`: compiled and started `target/debug/paradev-desktop` with no Tauri log errors; the desktop automation layer did not expose an inspectable native window.
- `PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 rtk bash scripts/run.bash --native-web --port 5181 --bridge-port 8766`: rendered the Project config tab against PIHC3 through the loopback bridge; verified PIHC3 paths, translated Build defaults, numeric `paradev.build.parallelism` spinbutton, and 0 console errors. Browser-only native-progress warnings remain expected outside Tauri.
- `rtk bash scripts/test.bash tests/test_desktop_api_selection.py tests/test_architecture.py tests/test_cli.py tests/test_native_web_bridge.py -q -k 'desktop_api_table or desktop_config_value or desktop_app_config or config_api or api_catalog_lists_generated_references or config_endpoints'`: 12 passed.
- `rtk bash scripts/test.bash tests/test_native_web_bridge.py -q`: 3 passed.
- `rtk npm --prefix apps/desktop run test:unit`: 42 files passed, 567 tests passed.
- `rtk npm --prefix apps/desktop run build`: passed; Vite reported the existing large-chunk warning.
- `rtk cargo fmt --manifest-path apps/desktop/src-tauri/Cargo.toml --check`: passed.
- `rtk cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml`: 24 passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/desktop/local.py src/paradev/desktop/__init__.py src/paradev/desktop/api.py src/paradev/surfaces/rest.py tests/test_desktop_api_selection.py tests/test_architecture.py tests/test_cli.py tests/test_native_web_bridge.py`: OK.
- `rtk bash scripts/flake.bash --ci`: passed.

PIHC3 status: clean on `v3.1`; no PIHC3 files changed.
