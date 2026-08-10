# 2026-06-30 04:40 - Config page desktop-only persistence

## Summary

- Stopped serializing CM-backed Config-page values into the desktop-only app settings payload.
- Kept desktop-only module preview defaults in app settings while excluding the CM-backed thumbnail cache row.
- Preserved reload compatibility by merging partial persisted module defaults onto the full current default row list.

## Verification

```bash
rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts src/configPage/ConfigPage.test.tsx -t "serializes only desktop-owned|preserves fallback module default"
rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts src/configPage/ConfigPage.test.tsx
rtk npm --prefix apps/desktop run test:unit
rtk npm --prefix apps/desktop run build
rtk git diff --check
rtk bash scripts/flake.bash --ci
rtk bash scripts/test.bash
rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri
```

Notes:

- The serializer test failed before implementation because no sanitized app-settings helper existed.
- The normalization test failed before implementation because partial persisted module defaults dropped the thumbnail-cache row.
- The standard fast gate passed with `1218 passed, 1 warning`.
- The desktop build still reports the existing Vite large-chunk warning.
- The Tauri PIHC3 smoke launched `target/debug/paradev-desktop` successfully.
