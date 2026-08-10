# PIHC3 Focus Authoring Template

Date: 2026-06-08

## Scope

Added the next small end-user authoring slice: a project-local template for creating a basic focus module in the current ParaDev focus scaffold.

## Result

- Added `pihc3:focus/basic` to `projects/PIHC3/paradev.yaml`.
- The template writes `meta.yaml`, `def.pdx`, and `main.loc` under `src/modules/focus/<object_id>/`.
- The default generated module uses:
  - `collection: PIHC3_MAIN`
  - `icon = GFX_goal_generic_political_pressure`
  - `cost = 10`
  - `x = 0`
  - `y = 0`
- Added SDK coverage in `tests/test_sdk_examples.py`.
- Updated `docs/user-manual/pihc3.md`.
- Added `projects/PIHC3/docs/migration/06-focuses.md`.

## Notes

- This is current ParaDev focus scaffold authoring support only.
- It is not a PIHC2 focus importer and does not claim parity with PIHC_dev full `focus_tree` files.
- The template uses a default collection so one SDK call creates a focus module and the build plans a `focus-tree.view.v1` artifact for future GUI/layout work.

## Verification

```bash
rtk bash scripts/test.bash tests/test_sdk_examples.py -q
rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py
rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py
rtk uv run paradev build projects/PIHC3 --emit-manifests --json
rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json
```

Observed results:

- `tests/test_sdk_examples.py`: 11 passed.
- Flake: 1 Python file unchanged.
- Heaven-style scan: OK, no banned imports.
- PIHC3 build: `module_count: 529`, `artifact_count: 26892`, `diagnostic_count: 0`, `error_count: 0`, `blocked: false`.
- Copy-root shadows: 0.
- Project-local templates listed by the SDK: `pihc3:event/country-basic`, `pihc3:focus/basic`, `pihc3:idea/legacy-current`, and `pihc3:trait/country-leader`.
