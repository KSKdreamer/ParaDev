# Desktop Canonical Removal Apply Progress

Date: 2026-06-08 11:48 CST

Linear: TAL-298, TAL-297

## Done

- Extended `POST /projects/{project_id}/drafts/apply` to accept `source_removals` alongside `source_edits`.
- Kept apply validation all-or-nothing: every write and removal path is project-contained and valid before any file is changed.
- Added `remove_file` rows to `paradev.rest.draft_apply.v1` apply responses.
- Let `paradev draft-apply --request` carry source removals through the existing JSON request file bridge.
- Updated Tauri `paradev_apply_project_draft` to pass both source edits and source removals to the CLI bridge.
- Added module editor model helpers for canonical source removals; shared `family_root` rows stay unsupported for removal apply so shared source files are not deleted from the GUI.
- Updated the module editor Apply handler so canonical removal drafts use the SDK-backed draft apply bridge and refresh desktop state afterward.
- Updated GUI copy plus architecture and GUI specs to mark canonical removal apply as implemented while image replacement and shared-file deletion remain future work.

## Verification

- Red checks: OpenAPI/REST/CLI tests first failed because `source_removals` was absent; model test first failed because removal helpers were absent; Rust test first failed because Tauri rejected empty source edits.
- `rtk bash scripts/test.bash tests/test_cli.py tests/test_architecture.py -q`: 23 passed, 1 skipped because `fastapi.testclient` is not installed.
- `rtk npm --prefix apps/desktop run test:model`: 10 passed.
- `rtk npm --prefix apps/desktop run build`: passed.
- `rtk bash -lc 'cd apps/desktop/src-tauri && cargo fmt'`: passed; `rtk bash` printed shell-profile zsh completion warnings but exited successfully.
- `rtk bash -lc 'cd apps/desktop/src-tauri && cargo test'`: 7 passed; `rtk bash` printed shell-profile zsh completion warnings but exited successfully.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/cli.py src/paradev/surfaces/cli.py src/paradev/surfaces/rest.py src/paradev/api/__init__.py tests/test_cli.py tests/test_architecture.py`: passed.
- `rtk bash scripts/flake.bash --ci --paths src/paradev/cli.py src/paradev/surfaces/cli.py src/paradev/surfaces/rest.py src/paradev/api/__init__.py tests/test_cli.py tests/test_architecture.py`: passed.
- Browser smoke on `http://127.0.0.1:4178`: app title `ParaDev`, nonblank shell, no framework overlay, no console warnings/errors, Ideas module tab opened with expected plain-Vite SDK browser fallback.
- `rtk uv run paradev build projects/PIHC3 --emit-manifests --json`: 529 modules, 26892 artifacts, 0 diagnostics, not blocked.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json`: 0 diagnostics.

## Risks Or Blockers

- Plain Vite still cannot exercise real Tauri project mutations because SDK browser data is unavailable outside the desktop shell; Rust and Python integration tests cover the write/delete path.
- `fastapi.testclient` remains absent in the default environment, so optional FastAPI endpoint execution is still covered by helper/OpenAPI tests rather than endpoint integration.
- Shared family-root removals remain intentionally unsupported in the GUI until a safer slot patch or parsed-object deletion route exists.
- Image replacement still needs a REST/OpenAPI apply route before the GUI can write it.

## Next

- Continue with image replacement apply or add a safer parsed/shared-file deletion route before enabling family-root removals.
