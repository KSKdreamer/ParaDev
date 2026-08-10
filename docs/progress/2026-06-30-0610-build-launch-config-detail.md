# Build Launch Config Detail

## Summary

- Marked the Build page HOI4 launch selector with `data-paradev-config-key="paradev.hoi4.launch_mode"`.
- Added a compact localized launch target detail below the selector so modders can see whether Run will use Steam/default or a configured local HOI4 root.
- Kept the Run action itself routed through the existing SDK-backed desktop launch bridge.

## Verification

- Red check: `rtk npm --prefix apps/desktop run test:unit -- src/buildPage/BuildPage.test.tsx -t "compact build actions"` failed because the Build page did not expose the launch config key or Steam/default detail.
- Red check: `rtk npm --prefix apps/desktop run test:unit -- src/buildPage/BuildPage.test.tsx -t "launch target"` failed before `buildLaunchModeDetail(...)` was exported.
- Green checks:
  - `rtk npm --prefix apps/desktop run test:unit -- src/buildPage/BuildPage.test.tsx -t "compact build actions"`
  - `rtk npm --prefix apps/desktop run test:unit -- src/buildPage/BuildPage.test.tsx -t "launch target"`
- `rtk npm --prefix apps/desktop run test:unit -- src/buildPage/BuildPage.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk git diff --check`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri`

The PIHC3 Tauri smoke reached the Vite-ready state and launched `target/debug/paradev-desktop`; no delayed startup output appeared before stopping the process.
