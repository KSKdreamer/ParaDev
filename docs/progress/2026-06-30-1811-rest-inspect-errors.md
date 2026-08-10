# REST Inspect Errors Progress

Date: 2026-06-30 18:11

Linear: ongoing usability goal

## Done

- Added native-web bridge coverage for invalid `/projects/inspect?kind=diagnostics` requests.
- Fixed `/projects/inspect` request injection under postponed annotations so FastAPI no longer treats `request` as a required query parameter.
- Normalized `OSError`, `ProjectManifestError`, and `ValueError` from SDK-backed project inspection into HTTP 400 responses with useful detail text.

## Verification

- Red first: `rtk bash scripts/test.bash tests/test_native_web_bridge.py -q -k inspect`
- `rtk bash scripts/test.bash tests/test_native_web_bridge.py -q -k inspect`
- `rtk bash scripts/test.bash tests/test_native_web_bridge.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/rest.py tests/test_native_web_bridge.py`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 47840`

## Risks Or Blockers

- The endpoint still returns the same simple FastAPI `detail` string shape as neighboring native bad-request handlers.

## Next

- Continue with stale post-write browser refresh behavior from the read-only subagent findings.
