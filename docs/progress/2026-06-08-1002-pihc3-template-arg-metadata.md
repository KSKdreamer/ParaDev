# PIHC3 Template Argument Metadata Progress

Date: 2026-06-08 10:02

Linear: TAL-297

## Done

- Added an `advanced` flag to SDK authoring template argument views.
- The flag is automatic: required and blank-default arguments are primary; arguments with defaults are advanced.
- This gives GUI and script clients a stable way to show the minimal create-module form first.
- Added coverage for built-in HoI4 template metadata and PIHC3 idea/trait primary fields.
- Updated SDK and modules user docs with the `advanced` contract.

## Verification

```bash
rtk bash scripts/test.bash tests/test_project.py tests/test_sdk_examples.py tests/test_cli.py -q
rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/templates.py tests/test_project.py tests/test_sdk_examples.py
rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/templates.py tests/test_project.py tests/test_sdk_examples.py
rtk uv run paradev build projects/PIHC3 --emit-manifests --json
rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json
```

Observed results:

- Targeted SDK/example/CLI tests: 142 passed.
- Flake: 3 Python files unchanged.
- Heaven-style scan: OK, no banned imports.
- PIHC3 build: `module_count: 529`, `artifact_count: 26892`, `diagnostic_count: 0`, `error_count: 0`, `blocked: false`.
- Copy-root shadows: 0.
- SDK template metadata probe reports PIHC3 idea/trait primary fields as `title` and `description`; derived/defaulted fields are advanced.

## Risks Or Blockers

- None for this slice.
- The current GUI still needs a follow-up slice to consume `advanced` and render a minimal create-module form.

## Next

- Wire GUI create-module forms to SDK template metadata, hiding advanced fields by default.
