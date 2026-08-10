# 2026-08-10 05:15 Packaged Same-Origin GUI

## Outcome

`paradev-gui` now launches the real ParaDev React application from an installed
Python package instead of printing a placeholder. The app uses one SDK-owned
FastAPI surface and one React/Vite frontend across the Python and Tauri hosts.

## Architecture

- `src/paradev/gui.py` composes `paradev.api.build_app()` with packaged static
  assets, binds only to loopback, selects a free port by default, and supports
  app-window, browser, and no-open modes.
- Runtime bridge discovery comes from a no-store same-origin bootstrap.
  Untrusted Host headers, cross-origin mutations, and cross-origin runtime URL
  injection are rejected.
- `apps/desktop` remains the only frontend source. `scripts/sync-gui.mjs`
  atomically synchronizes its production output into
  `src/paradev/resources/gui`, and `npm run check:package` compares exact file
  digests.
- FastAPI and Uvicorn are base runtime dependencies because the installed GUI
  entry point is a base product surface.
- The browser-hosted macOS app can open the native project folder picker through
  `POST /desktop/select-project`; project parsing and validation still belong to
  the SDK.

## Installability Evidence

- Wheel artifact:
  `dist/python/paradev-0.1.0.0.dev0-py3-none-any.whl`.
- Wheel inventory: 143 entries, 22 GUI resources, zero `.pyc` or
  `__pycache__` entries.
- Fresh Python 3.12 environment: installed the wheel and 92 resolved
  dependencies, then ran the installed `paradev-gui` entry point outside the
  repository checkout.
- Live probes passed for `/health`, `/paradev-runtime-config.js`,
  `/desktop/state?include_browser=false`, and the hashed JavaScript entry.
- The clean first-run state returned no projects and no diagnostics, ready for
  the macOS Open Project flow.

This is a reproducible wheel-hosted application, not yet a standalone `.app`
installer. A user still needs a supported Python installation until the next
unsigned native wrapper/installer slice.

## Verification

- `rtk bash scripts/test.bash`: 2,435 passed, 9 native-Windows skips.
- `rtk npm test`: 1,513 passed.
- `rtk npm run build`: production build and 22-file package sync passed.
- `rtk npm run check:package`: exact source/package digest parity passed.
- `rtk bash scripts/sync-env.bash --check`: dependency and generated metadata
  are current.
- PIHC3 source layout: 14,574 modules, 70 module families, 90 collections,
  36,469 source files, one visible metadata file, and zero errors.

## Remaining Release Gaps

- Produce the unsigned standalone macOS app wrapper so users do not install
  Python manually.
- Exercise the folder picker and a PIHC3 edit/build flow in the rendered
  wheel-hosted UI, then add that flow to an automated clean-install smoke.
- The existing 1.8 GB verified PIHC3 project archive remains a separate release
  artifact; this wheel supports selecting an extracted PIHC3 folder but does
  not embed that archive.
- Cached full-build performance remains dominated by full-project planning,
  per-artifact staging, and per-event JSONL reopen work.
