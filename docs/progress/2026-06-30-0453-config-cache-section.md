# 2026-06-30 04:53 - Config cache section split

## Summary

- Split the CM-backed thumbnail cache limit out of the local module preview-size panel on the Config page.
- Kept the existing `moduleDefaults` data shape so the desktop config bridge still writes `paradev.desktop.thumbnail_cache.max_kb` through the same SDK-backed path.
- Added English and Chinese copy for the new thumbnail cache section and kept row rendering shared.

## Verification

```bash
rtk npm --prefix apps/desktop run test:unit -- src/configPage/ConfigPage.test.tsx -t "separates local preview defaults"
rtk npm --prefix apps/desktop run test:unit -- src/configPage/ConfigPage.test.tsx src/App.test.ts src/i18n/locales.test.ts
rtk npm --prefix apps/desktop run test:unit
rtk npm --prefix apps/desktop run build
rtk bash scripts/flake.bash --ci
rtk bash scripts/test.bash
rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri
```

Notes:

- The new split test failed before implementation because the `Thumbnail cache` panel did not exist.
- The standard fast gate passed with `1218 passed`.
- The desktop build still reports the existing Vite large-chunk warning.
- The Tauri PIHC3 smoke launched `target/debug/paradev-desktop` successfully. Computer Use could not inspect the dev window because macOS accessibility returned `AXError.cannotComplete` / timeout for the ParaDev app handle.
