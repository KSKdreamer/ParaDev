# 2026-06-30 03:46 - Translation alias hint i18n

## Summary

- Localized the module entity translation alias helper instead of rendering the hard-coded `(@ = OBJECT_ID)` text.
- Added English and Chinese locale keys for the current-entity `@` alias hint.
- Updated the Chinese module entity details test to guard against the hard-coded helper returning.

## Verification

```bash
rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/ModuleEntityDetails.test.tsx
rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/ModuleEntityDetails.test.tsx src/i18n/locales.test.ts
rtk git diff --check
rtk npm --prefix apps/desktop run test:unit
rtk npm --prefix apps/desktop run build
rtk bash scripts/flake.bash --ci
rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri
```

Notes:

- The first focused test run failed before implementation because the Chinese markup still rendered `(@ = IDEA_BETA)`.
- The Tauri PIHC3 smoke launched `target/debug/paradev-desktop` and produced no extra runtime output during the smoke window.
- The desktop build still reports the existing Vite large-chunk warning.
