# PIHC3 Event Authoring Template

Date: 2026-06-08

## Scope

Added the next small end-user authoring slice after idea and trait cleanup: a project-local template for creating a standalone PIHC3 country event.

## Result

- Added `pihc3:event/country-basic` to `projects/PIHC3/paradev.yaml`.
- The template writes `meta.yaml`, `def.pdx`, and `main.loc` under `src/modules/event/<object_id>/`.
- The default generated PDX uses:
  - `add_namespace = <object_id>`
  - `country_event = { id = <object_id>.1 }`
  - `is_triggered_only = yes`
  - one localized option
- Added SDK coverage in `tests/test_sdk_examples.py`.
- Updated `docs/user-manual/pihc3.md`.
- Added `projects/PIHC3/docs/migration/05-events.md`.

## Notes

- This is authoring support only, not a PIHC2 event importer or parity claim.
- The template intentionally avoids collection setup so the first event workflow is one SDK call and one module folder.
- Character and technology module creation still require compiler-family work before PIHC3 can expose project-local templates for them.

## Verification

```bash
rtk bash scripts/test.bash tests/test_sdk_examples.py -q
rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py
rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py
rtk uv run paradev build projects/PIHC3 --emit-manifests --json
rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json
```

Observed results:

- `tests/test_sdk_examples.py`: 10 passed.
- Flake: 1 Python file unchanged.
- Heaven-style scan: OK, no banned imports.
- PIHC3 build: `module_count: 529`, `artifact_count: 26892`, `diagnostic_count: 0`, `error_count: 0`, `blocked: false`.
- Copy-root shadows: 0.
