# 2026-06-30 05:39 - Config page key aliases

## Summary

- Rewired config page controls to use `DESKTOP_CONFIG_KEYS` from `apps/desktop/src/desktopConfig.ts` instead of embedding raw desktop `CM_PARADEV` keys in JSX.
- Tightened config route field props and configurable module-default keys to the generated `DesktopConfigKey` union.
- Added a source guard so future config page controls cannot reintroduce raw `paradev.*` config-key literals in `ConfigPage.tsx` or `configPage/model.ts`.

## Verification

```bash
rtk npm --prefix apps/desktop run test:unit -- src/configPage/ConfigPage.test.tsx -t "shared key aliases"
rtk npm --prefix apps/desktop run test:unit -- src/configPage/ConfigPage.test.tsx
rtk npm --prefix apps/desktop run test:unit
rtk npm --prefix apps/desktop run build
rtk git diff --check
rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri
```

Notes:

- The new source guard failed first on raw `configKey="paradev.*"` literals in `ConfigPage.tsx`.
- The full desktop unit suite passed with `683 passed`; the production build passed with the existing large-chunk warning.
- The PIHC3 Tauri smoke reached the Vite-ready and `target/debug/paradev-desktop` running state, then was stopped with Ctrl-C after a quiet startup window.
