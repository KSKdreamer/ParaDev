# Desktop Image Replacement Apply Progress

Date: 2026-06-08 12:03 CST

Linear: TAL-298, TAL-297

## Done

- Extended `POST /projects/{project_id}/drafts/apply` to accept `source_replacements` alongside `source_edits` and `source_removals`.
- Added base64 decoding and `replace_bytes` response rows, with all target paths validated before any write/remove operation runs.
- Let `paradev draft-apply --request` carry source replacements through the existing JSON request file bridge.
- Updated Tauri `paradev_apply_project_draft` to accept React `sourceReplacements`, validate replacement paths/content, and write backend `content_base64` request rows.
- Stored selected PNG/JPEG/WebP bytes in the module editor image draft instead of only a blob preview URL.
- Added module editor model helpers that map image drafts to source-byte replacement requests and clear applied image drafts afterward.
- Updated the module editor Apply handler so selected image drafts use the SDK-backed draft apply bridge and refresh desktop state afterward.
- Updated GUI copy plus architecture and GUI specs to mark selected image replacement bytes as implemented while crop metadata and image format conversion remain pending.

## Verification

- Red checks: OpenAPI/REST/CLI tests first failed because `source_replacements` was absent; model test first failed because image replacement helpers were absent; Rust test first failed because Tauri had no replacement request field.
- Focused green checks:
  - `rtk bash scripts/test.bash tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_rest_apply_project_draft_replaces_source_bytes tests/test_architecture.py::test_rest_apply_project_draft_rejects_outside_source_replacement_before_writing tests/test_cli.py::test_draft_apply_cli_replaces_source_bytes -q`: 4 passed.
  - `rtk npm --prefix apps/desktop run test:model`: 11 passed.
  - `rtk cargo test apply_project_draft_command_replaces_source_bytes` from `apps/desktop/src-tauri`: 1 passed.
- `rtk bash scripts/test.bash tests/test_cli.py tests/test_architecture.py -q`: 26 passed, 1 skipped because `fastapi.testclient` is not installed.
- `rtk npm --prefix apps/desktop run test:model`: 11 passed.
- `rtk npm --prefix apps/desktop run build`: passed.
- `rtk cargo fmt` from `apps/desktop/src-tauri`: passed.
- `rtk cargo test` from `apps/desktop/src-tauri`: 8 passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/cli.py src/paradev/surfaces/rest.py tests/test_cli.py tests/test_architecture.py`: passed.
- `rtk bash scripts/flake.bash --ci --paths src/paradev/cli.py src/paradev/surfaces/rest.py tests/test_cli.py tests/test_architecture.py`: passed.
- PIHC3 build through the SDK: 529 modules, 0 collections, 0 dependencies, 26892 artifacts, 0 diagnostics, 0 errors, not blocked.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json`: 0 diagnostics.
- Browser smoke on `http://127.0.0.1:4178`: app title `ParaDev`, nonblank shell, no framework overlay, no console warnings/errors, Ideas module tab opened with the expected plain-Vite SDK browser fallback.

## Risks Or Blockers

- Plain Vite still cannot exercise real Tauri project mutations because SDK browser data and draft apply require the desktop shell; Rust and Python integration tests cover the write path.
- `fastapi.testclient` remains absent in the default environment, so optional FastAPI endpoint execution is still covered by helper/OpenAPI tests rather than endpoint integration.
- Image crop metadata remains draft-only; the apply path currently writes selected bytes exactly as dropped and does not crop or convert formats.
- The image draft UI targets the first image source slot for the selected entity. Multi-image slot targeting can be added once PIHC3 has a concrete need.

## Next

- Continue with safer parsed/shared-file deletion routes or add image crop/format conversion before exposing more asset workflows.
