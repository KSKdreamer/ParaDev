# PIHC3 Desktop Create Form Progress

Date: 2026-06-08 10:24

Linear: TAL-297

## Done

- Added a compact module-create form to the desktop module entity list.
- The form shows object id and non-advanced template arguments first, and hides defaulted advanced fields behind one optional icon control.
- Create drafts now merge visible input with template defaults, including rendered defaults such as `{family_tag}`.
- New local drafts carry their scaffold intent under `drafts.create`, including template id, merged values, and advanced field names.
- Blank object id input keeps the zero-typing draft path by using the generated family draft id.
- Updated the GUI spec to make the create-form contract current rather than future-facing.

## Verification

```bash
npm run test:model
npm run build
rtk bash scripts/test.bash tests/test_cli.py::test_desktop_state_cli_returns_projects_and_browser_payload tests/test_project.py::test_project_templates_list_builtin_authoring_templates tests/test_sdk_examples.py::test_pihc3_template_args_mark_only_primary_create_fields -q
rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/project.py tests/test_cli.py
rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py tests/test_cli.py
rtk uv run paradev build projects/PIHC3 --emit-manifests --json
rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json
```

Observed results:

- Desktop model tests: 6 passed.
- Desktop TypeScript/Vite build: passed.
- Browser web-shell smoke on `http://127.0.0.1:4178/`: page rendered, Ideas tab opened, no console errors or warnings. The plain Vite fallback still reports `SDK browser unavailable`, so create-form interaction remains covered by model/build tests until Tauri or REST data is available in-browser.
- Targeted SDK/CLI/template tests: 3 passed.
- Flake: 2 Python files unchanged.
- Heaven-style scan: OK, no banned imports.
- PIHC3 build: `module_count: 529`, `artifact_count: 26892`, `diagnostic_count: 0`, `error_count: 0`, `blocked: false`.
- Copy-root shadows: 0.

## Risks Or Blockers

- Actual write/apply behavior remains blocked on the REST/OpenAPI draft mutation path.
- Browser validation cannot exercise SDK-backed module data in plain Vite because the SDK browser payload is currently supplied by Tauri.

## Next

- Add the REST/OpenAPI draft creation endpoint so the GUI can turn `drafts.create` into a real scaffold plan and write action.
