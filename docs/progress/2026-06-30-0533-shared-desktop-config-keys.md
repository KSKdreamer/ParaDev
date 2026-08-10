# 2026-06-30 05:33 - Shared desktop config keys

## Summary

- Moved the desktop GUI's named `CM_PARADEV` key aliases into `apps/desktop/src/desktopConfig.ts`, backed by the generated SDK-owned desktop config-key tuple.
- Updated `App.tsx` and the Build page to consume the shared config-key facade instead of owning local bridge-key constants.
- Removed HOI4 launch config constants from the pure build model so build model logic stays separate from desktop bridge details.

## Verification

```bash
rtk npm --prefix apps/desktop run test:unit -- src/buildPage/buildPageModel.test.ts -t "HOI4"
rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts -t "named desktop config map"
rtk npm --prefix apps/desktop run test:unit
rtk npm --prefix apps/desktop run build
rtk git diff --check
rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri
```

Notes:

- The initial targeted test failed first because `../desktopConfig` did not exist yet.
- The full desktop unit suite passed with `682 passed`; the production build passed with the existing large-chunk warning.
- The PIHC3 Tauri smoke reached the Vite-ready and `target/debug/paradev-desktop` running state, then was stopped with Ctrl-C after a quiet startup window.
