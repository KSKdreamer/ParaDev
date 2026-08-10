# Config Path Status Progress

## Summary

- Added the SDK-owned `desktop_path_status(...)` desktop facade and exposed it through REST `/desktop/path-status`, the Tauri command bridge, and desktop TypeScript service helpers.
- Updated Config > Projects so project root, source roots, output, build cache, and HOI4 root show compact status chips before path-opening actions.
- Disabled open buttons for SDK-reported non-openable paths, treated generated output/cache paths as neutral when missing, and treated an empty HOI4 root as Steam/default instead of an error.
- Synchronized generated API references plus architecture and GUI specs so path status remains a Python SDK contract, not React-owned filesystem logic.

## PIHC3 Smoke

- Loaded the real `projects/PIHC3` desktop state with `--no-browser`.
- Verified `desktop_path_status(...)` reports PIHC3 project root, source root, generated mod output, and build cache as existing, readable directories.
- Ran bounded `scripts/run.bash --tauri` with `PARADEV_PROJECTS=projects/PIHC3`; Vite, Tauri dev, and the Rust dev build reached startup markers and were terminated cleanly by the harness.
- Browser-inclusive PIHC3 `desktop-state` remained heavy after roughly 90 seconds; that is a separate browser payload performance issue, not part of this path-status slice.

## Verification

- `rtk bash scripts/test.bash`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml`
- `rtk cargo fmt --manifest-path apps/desktop/src-tauri/Cargo.toml --check`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src tests`
