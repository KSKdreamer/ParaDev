# Native Web Bridge Build Smoke

## Summary

- Added a loopback native web bridge path so the browser-hosted desktop UI can call the same local file, build, open-path, and HoI4 launch helpers as the Tauri shell when `VITE_PARADEV_NATIVE_BRIDGE_URL` is configured.
- Kept rendered GUI debugging defaulted to the native Tauri view in `AGENTS.md`; `scripts/run.bash --native-web` is now the explicit bridge-backed browser mode.
- Fixed a transient macOS full-rebuild cleanup failure by retrying generated-root deletion before artifact emission.
- Completed a full PIHC3 Build-page lifecycle run through `/desktop/builds`: `bridge-build-d1786051595f` reached `complete` at 100%, exit code `0`, with 16,596 modules, 78 collections, and 37,192 artifacts.
- Exercised `/desktop/run-hoi4` for PIHC3 in Steam mode; it returned `open steam://rungameid/394360`.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/services/paradev.test.ts`
- `rtk npm --prefix apps/desktop run build`
- `rtk bash scripts/test.bash tests/test_native_web_bridge.py -q`
- `rtk bash scripts/test.bash tests/test_project_build.py::test_project_build_full_rebuild_retries_transient_output_delete_errors -q`
- `rtk bash -n scripts/run.bash`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/rest.py src/paradev/sdk/project.py tests/test_native_web_bridge.py tests/test_project_build.py`
- `rtk bash scripts/run.bash --native-web --port 5197 --bridge-port 8767` smoke with `/health`, `/`, and `/desktop/state?project_path=projects%2FPIHC3&include_browser=false`.
