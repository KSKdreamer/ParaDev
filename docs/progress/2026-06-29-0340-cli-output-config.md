# CLI Output Config Page

Time: 2026-06-29 03:40 CST

Continued the GUI usability/API-alignment loop by exposing `CM_PARADEV["paradev.cli.output"]` as a real SDK-owned command default instead of leaving it as an unused default.

- Made CLI structured output honor `paradev.cli.output = "json"` when no local `--json` flag is passed.
- Added `paradev.cli.output` to the desktop config-value allowlist with `yaml`/`json` validation.
- Added a General-page Command defaults panel with translated English/Chinese labels and a compact YAML/JSON select that persists through `readConfigValue(...)` / `writeConfigValue(...)`.
- Updated architecture and GUI docs so real runtime config keys include both `paradev.build.parallelism` and `paradev.cli.output`.

Subagent notes:

- Config audit confirmed `paradev.cli.output` is the only remaining default `CM_PARADEV` key that is both real and appropriate for a small GUI config slice.
- Visual/translation audit found a separate next slice: Chinese fallback labels in common workbench states, Config Models labels, and status labels.

Validation:

- `PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 rtk bash scripts/run.bash --tauri`: compiled and started `target/debug/paradev-desktop` with no Tauri log errors; the desktop accessibility layer returned `AXError.cannotComplete`.
- `PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 rtk bash scripts/run.bash --native-web --port 5181 --bridge-port 8766`: rendered Config General against PIHC3 through the loopback bridge; verified SDK state loaded, `paradev.cli.output` appeared as YAML/JSON select, selecting JSON wrote `/desktop/config-value` payload `{"key":"paradev.cli.output","value":"json"}`, and restored YAML after the check. Browser-only native-progress warnings remain expected outside Tauri.
- `rtk bash scripts/test.bash tests/test_desktop_api_selection.py tests/test_cli.py -q -k 'desktop_config_value or cli_output_config'`: 5 passed.
- `rtk npm --prefix apps/desktop run test:unit`: 42 files passed, 569 tests passed.
- `rtk npm --prefix apps/desktop run build`: passed; Vite reported the existing large-chunk warning.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/desktop/local.py src/paradev/cli.py tests/test_desktop_api_selection.py tests/test_cli.py`: OK.
- `rtk bash scripts/flake.bash --ci`: passed.
- `rtk bash scripts/test.bash`: 1158 passed, 1 warning.

PIHC3 status: clean on `v3.1`; no PIHC3 files changed.
