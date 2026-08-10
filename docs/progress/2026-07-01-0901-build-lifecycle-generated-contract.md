# 2026-07-01 09:01 - Build lifecycle generated contract

## Summary

Removed the hand-maintained Build page mirror of generated frontend API metadata
for `build.start`, `build.status`, and `build.interrupt`. The GUI now keeps only
the action-name to operation-id map and derives confirmation, SDK, REST, payload,
and summary fields from the checked-in SDK-generated frontend API contract.

This keeps the Build page wrapper closer to the Python SDK/front-end API source
of truth while preserving the existing dynamic import path for action panel
execution helpers.

## Verification

- Red first: `rtk npm --prefix apps/desktop run test:unit -- --run src/buildPage/BuildPage.test.tsx -t "derives build lifecycle contracts"` failed on the hardcoded `confirmationTitle`/`summary`/`sdkCall` mirror.
- `rtk npm --prefix apps/desktop run test:unit -- --run src/buildPage/BuildPage.test.tsx -t "derives build lifecycle contracts"`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/buildPage/BuildPage.test.tsx src/data/frontendApi.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build` passed with only the pre-existing large-chunk warning.
- `rtk env PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 bash scripts/run.bash --tauri --port 47852` reached Vite ready, finished Cargo build, launched `target/debug/paradev-desktop`, and showed no late startup output before manual stop.
