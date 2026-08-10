# PIHC3 Technology Authoring Template

Date: 2026-06-08

## Scope

Added the next end-user authoring slice: a project-local `technology` build family and a basic technology template for PIHC3.

## Result

- Added `families.technology` to `projects/PIHC3/paradev.yaml`.
- The family is manifest-local and uses the generic `simple_source` compiler.
- Technology modules emit:
  - `common/technologies/{object_id}.txt`
  - `localisation/{language_folder}/{object_id}_{language}.yml`
- The family consumes `def.pdx` and `*.loc`, and requires `<object_id>` and `<object_id>_desc` localization keys when localization is authored.
- Added `pihc3:technology/basic`.
- The template writes `meta.yaml`, `def.pdx`, and `main.loc` under `src/modules/technology/<object_id>/`.
- Added SDK coverage in `tests/test_sdk_examples.py`.
- Updated `docs/user-manual/pihc3.md`.
- Added `projects/PIHC3/docs/migration/08-technologies.md`.

## Notes

- This is a basic technology shell only.
- It follows observed PIHC_dev one-file-per-technology output with a top-level `technologies = { ... }` wrapper.
- It does not import PIHC2 `resources/technologies`.
- It does not generate technology icons, dependencies, paths, equipment unlocks, subunit unlocks, stat blocks, or allow gates.
- Project-local templates now cover the user-named starter families: idea, focus, event, character, trait, and technology.

## Verification

```bash
rtk bash scripts/test.bash tests/test_sdk_examples.py -q
rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py
rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py
rtk uv run paradev build projects/PIHC3 --emit-manifests --json
rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json
```

Observed results:

- `tests/test_sdk_examples.py`: 13 passed.
- Flake: 1 Python file unchanged.
- Heaven-style scan: OK, no banned imports.
- PIHC3 build: `module_count: 529`, `artifact_count: 26892`, `diagnostic_count: 0`, `error_count: 0`, `blocked: false`.
- Copy-root shadows: 0.
- SDK family list includes `technology` as a project-local `simple_source` family.
- Project-local templates listed by the SDK: `pihc3:character/basic`, `pihc3:event/country-basic`, `pihc3:focus/basic`, `pihc3:idea/legacy-current`, `pihc3:technology/basic`, and `pihc3:trait/country-leader`.
