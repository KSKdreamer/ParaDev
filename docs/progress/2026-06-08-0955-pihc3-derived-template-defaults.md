# PIHC3 Derived Template Defaults Progress

Date: 2026-06-08 09:55

Linear: TAL-297

## Done

- Added formatted template argument defaults in the SDK scaffold renderer.
- Added the generic scaffold value `{family_tag}`, derived by stripping a matching uppercase family prefix from `object_id`.
- Updated PIHC3 idea and trait templates so `legacy_tag` defaults to `{family_tag}` instead of requiring a user-supplied value.
- Kept explicit `legacy_tag` overrides working for parity cases.
- Updated PIHC3 user docs and migration notes so normal idea/trait creation no longer asks for `legacy_tag`.

## Verification

```bash
rtk bash scripts/test.bash tests/test_project.py tests/test_sdk_examples.py -q
rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/templates.py tests/test_project.py tests/test_sdk_examples.py
rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/templates.py tests/test_project.py tests/test_sdk_examples.py
rtk uv run paradev build projects/PIHC3 --emit-manifests --json
rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json
```

Observed results:

- Targeted SDK/example tests: 130 passed.
- Flake: 3 Python files unchanged.
- Heaven-style scan: OK, no banned imports.
- PIHC3 build: `module_count: 529`, `artifact_count: 26892`, `diagnostic_count: 0`, `error_count: 0`, `blocked: false`.
- Copy-root shadows: 0.
- SDK template metadata reports `legacy_tag required=False default={family_tag}` for `pihc3:idea/legacy-current` and `pihc3:trait/country-leader`.
- No-write SDK probe resolved `idea` and `trait` shorthands without `legacy_tag` and returned unblocked plans.

## Risks Or Blockers

- None for this slice.
- Formatted defaults intentionally use Python-style `{name}` placeholders and known scaffold values only.

## Next

- Continue reducing create-module friction around GUI form metadata and starter-module argument visibility.
