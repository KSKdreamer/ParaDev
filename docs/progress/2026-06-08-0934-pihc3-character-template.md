# PIHC3 Character Authoring Template

Date: 2026-06-08

## Scope

Added the next end-user authoring slice: a project-local `character` build family and a basic character template for PIHC3.

## Result

- Added `families.character` to `projects/PIHC3/paradev.yaml`.
- The family is manifest-local and uses the generic `simple_source` compiler.
- Character modules emit:
  - `common/characters/{object_id}.txt`
  - `localisation/{language_folder}/{object_id}_{language}.yml`
- The family consumes `def.pdx` and `*.loc`, and requires `_NAME` and `_DESC` localization keys when localization is authored.
- Added `pihc3:character/basic`.
- The template writes `meta.yaml`, `def.pdx`, and `main.loc` under `src/modules/character/<object_id>/`.
- Added SDK coverage in `tests/test_sdk_examples.py`.
- Updated `docs/user-manual/pihc3.md`.
- Added `projects/PIHC3/docs/migration/07-characters.md`.

## Notes

- This is a basic character shell only.
- It does not import PIHC2 `resources/characters`.
- It does not generate portraits or role blocks such as `advisor`, `country_leader`, `corps_commander`, or `navy_leader`.
- The family stays project-local so PIHC-specific behavior does not enter `src/paradev/` before the broader HoI4 character compiler shape is proven.

## Verification

```bash
rtk bash scripts/test.bash tests/test_sdk_examples.py -q
rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py
rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py
rtk uv run paradev build projects/PIHC3 --emit-manifests --json
rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json
```

Observed results:

- `tests/test_sdk_examples.py`: 12 passed.
- Flake: 1 Python file unchanged.
- Heaven-style scan: OK, no banned imports.
- PIHC3 build: `module_count: 529`, `artifact_count: 26892`, `diagnostic_count: 0`, `error_count: 0`, `blocked: false`.
- Copy-root shadows: 0.
- SDK family list includes `character` as a project-local `simple_source` family.
- Project-local templates listed by the SDK: `pihc3:character/basic`, `pihc3:event/country-basic`, `pihc3:focus/basic`, `pihc3:idea/legacy-current`, and `pihc3:trait/country-leader`.
