# Desktop Source Text Apply Progress

Date: 2026-06-08 11:39 CST

Linear: TAL-298, TAL-297

## Done

- Added `paradev draft-apply` as a CLI bridge over the SDK-backed REST draft apply helper.
- Added the Tauri `paradev_apply_project_draft` command, which sends source edits through a temporary JSON request file and shells the CLI bridge.
- Added desktop service/types for `paradev.rest.draft_apply.v1` source-text apply payloads.
- Updated the module editor model to build source text edits from modified entities and clear only written text drafts after apply, preserving image drafts.
- Updated the module editor Apply handler so the same button writes either new scaffold drafts or existing source text edits.
- Cleared the source text cache after successful text apply so the editor reloads written text from disk.
- Updated GUI and architecture docs to mark source text apply as implemented while removal and image apply remain draft-only.

## Verification

- Red checks: CLI test first failed because `draft-apply` did not exist; Rust test first failed because `paradev_apply_project_draft` and request structs did not exist; model test first failed because the source-apply helpers did not exist.
- `rtk bash scripts/test.bash tests/test_cli.py tests/test_architecture.py -q`: 20 passed, 1 skipped because `fastapi.testclient` is not installed.
- `rtk npm --prefix apps/desktop run test:model`: 9 passed.
- `rtk npm --prefix apps/desktop run build`: passed.
- `rtk bash -lc 'cd apps/desktop/src-tauri && cargo fmt'`: passed; `rtk bash` printed shell-profile zsh completion warnings but exited successfully.
- `rtk bash -lc 'cd apps/desktop/src-tauri && cargo test'`: 6 passed; `rtk bash` printed shell-profile zsh completion warnings but exited successfully.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/cli.py src/paradev/surfaces/cli.py src/paradev/surfaces/rest.py src/paradev/api/__init__.py tests/test_cli.py tests/test_architecture.py`: passed.
- `rtk bash scripts/flake.bash --ci --paths src/paradev/cli.py src/paradev/surfaces/cli.py src/paradev/surfaces/rest.py src/paradev/api/__init__.py tests/test_cli.py tests/test_architecture.py`: passed.
- Browser smoke on `http://127.0.0.1:4178`: app title `ParaDev`, nonblank shell, no console warnings/errors, Ideas module tab opened and showed expected plain-Vite SDK browser fallback.
- `rtk uv run paradev build projects/PIHC3 --emit-manifests --json`: 529 modules, 26892 artifacts, 0 diagnostics, not blocked.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json`: 0 diagnostics.

## Risks Or Blockers

- Plain Vite cannot exercise Tauri source apply because SDK browser data is unavailable outside the desktop shell; the write path is covered by Rust and Python integration tests.
- `fastapi.testclient` remains absent in the default environment, so optional FastAPI endpoint execution is still covered by helper/OpenAPI tests rather than endpoint integration.
- Removal drafts and image replacement still need REST/OpenAPI apply routes before the GUI can write them.

## Next

- Continue with generic REST apply coverage for removal or image replacement, or add a lightweight desktop/Tauri manual smoke path for source text edits against PIHC3 when the desktop shell is running.
