# 2026-07-01 07:25 - Build page config metadata

## Summary

Aligned the Build page with the SDK-owned desktop config metadata generated from Python. Build fallback values for `paradev.hoi4.launch_mode`, `paradev.build.parallelism`, and `paradev.build.strict_metadata` now come from the generated desktop config contract instead of duplicated React literals. The Build page launch-mode select renders generated choices, and the build parallelism control uses the generated minimum.

Extended the same generated minimum helper to Config page numeric controls for SDK-backed settings, while keeping local-only module preview sizes local. Added tests that assert BuildPage/ConfigPage defaults, choices, and minimums follow `PARADEV_DESKTOP_CONFIG_ROWS` and `PARADEV_DESKTOP_CONFIG_DEFAULTS`.

Read-only PIHC3 minimization audit found a safe next PIHC3 slice: two decision collections (`DECISION_CATEGORY_C08_WASTELAND_DEVELOP` and `DECISION_CATEGORY_C08_EAST_ROUTE`) still have `title: TODO` and no root image. A larger later pilot is technology icon migration from `legacy/default.png` into canonical root images, after confirming compiler dependencies.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- --run src/buildPage/buildPageModel.test.ts src/buildPage/BuildPage.test.tsx src/configPage/ConfigPage.test.tsx`
- `rtk npm --prefix apps/desktop run build`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk bash scripts/sync-env.bash --check`
- `rtk bash scripts/flake.bash --ci`
- `rtk git diff --check`
- `rtk env PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 bash scripts/run.bash --tauri --port 47848` reached Vite ready, Cargo finished, and `target/debug/paradev-desktop` started without late startup output before manual stop.
