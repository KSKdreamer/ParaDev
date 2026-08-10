# Installed PIHC3 GUI Builds

Status: completed slice

Date: 2026-08-10

## Outcome

The wheel-hosted ParaDev app now completes real PIHC3 builds with the Python
runtime that owns the installed package. A user-launched `paradev-gui` process
no longer depends on a developer checkout, `uv`, or a `paradev` executable on
`PATH` when the GUI starts a build.

The rendered app was exercised against the live PIHC3 project after installing
the wheel into a clean Python 3.12 environment. It discovered 14,574 modules,
90 collections, and 36,469 source files with zero diagnostics, then completed:

- a cached whole-project build in 55 seconds;
- a Military Industrial Organizations family-partial build in 50 seconds; and
- a `military_industrial_organization/ai_bonus_weights` module-partial build in
  46 seconds.

The earlier published-wheel clean/full/cached/family/module output-parity matrix
remains the compilation baseline. This slice specifically proves that the
installed rendered app can invoke the same compiler path.

## Stability fixes

- Native-web builds translate the Tauri-facing `uv run paradev` command into
  `sys.executable -m paradev`, and `paradev.__main__` is now packaged as the
  installed module entry point.
- The build subprocess runs with the selected project as its working directory,
  removing the final repository-layout assumption from this path.
- Focus diagrams now treat Focus collections as tree scopes and resolve their
  standalone child modules from the Registry projection. The rendered selector
  shows 28 real trees rather than 766 mixed collection/module rows.
- The same clean-wheel session rendered C01_MAIN with 83 nodes and 101 links,
  the Technology tree with 300 nodes and 388 links, and a selected MIO
  organization with 15 traits and 30 links.

## Reproducible artifact

`scripts/build-wheel.bash` is now the authoritative wheel build path. It builds
the desktop frontend, atomically synchronizes the package resources, removes
only setuptools' generated `build/` directory, builds into a temporary output
directory, and rejects missing or stale GUI files before publishing the wheel.

- Artifact: `dist/python/paradev-0.1.0.0.dev0-py3-none-any.whl`
- SHA-256: `95da24ea641c3690add1859bd97aee6142cd54eba4d23cbae32143d12efcef4b`
- Inventory: 144 files, including exactly 22 GUI files and
  `paradev/__main__.py`.
- Runtime dependencies in the clean reinstall include HeavenBase 0.1.2.2,
  FastMCP 4.0.0b2, and MCP 2.0.0.

## Verification

- `rtk bash scripts/test.bash`: 2,436 passed, 9 native-Windows skips.
- `rtk npm test`: 1,515 passed.
- Focus/Module Editor diagram gate: 31 passed.
- Native-web/Desktop build lifecycle gate: 93 passed.
- PIHC3 retired component/legacy/inactive source guard: 11 passed.
- `rtk npm run check:package`: exact 22-file GUI digest parity passed.
- `rtk bash scripts/sync-env.bash --check`: lock, generated metadata, and
  canonical README mirrors are current.
- `rtk git diff --check`: passed.

## Remaining app work

- Whole-project planning still dominates cached and targeted builds; the
  current installed timings are usable but not yet interaction-fast.
- Add an automated browser smoke that installs the wheel and executes the same
  whole/family/module build lifecycle without relying on this manual rendered
  checkpoint.
- Continue reducing large-family Guided-form density, especially support-style
  MIO modules, while keeping the Registry as the single semantic owner.
- A standalone unsigned `.app` wrapper remains separate release work. Windows
  integration and macOS game launch are intentionally outside the current app
  stability slice.
