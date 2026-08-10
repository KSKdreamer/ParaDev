# PIHC3 Family Shorthand Scaffold Progress

Date: 2026-06-08 09:46

Linear: TAL-297

## Done

- Added family shorthand resolution to `Project.scaffold_module(...)`.
- Exact template ids still work.
- A family shorthand such as `idea` resolves to a single matching template.
- If one project-local template matches a family, it is preferred over built-in templates.
- Ambiguous family shorthand now raises a contextual `ValueError` asking for a full template id.
- Updated CLI help and CLI coverage so `paradev scaffold <project> idea <object_id>` uses the same SDK behavior.
- Updated SDK, module, and PIHC3 user docs to show the simpler family-first authoring path.

## Verification

```bash
rtk bash scripts/test.bash tests/test_project.py tests/test_cli.py tests/test_sdk_examples.py -q
rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/project.py src/paradev/cli.py tests/test_project.py tests/test_cli.py tests/test_sdk_examples.py
rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py src/paradev/cli.py tests/test_project.py tests/test_cli.py tests/test_sdk_examples.py
rtk uv run paradev build projects/PIHC3 --emit-manifests --json
rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json
```

Observed results:

- Targeted SDK/CLI/example tests: 139 passed.
- Flake: 5 Python files unchanged.
- Heaven-style scan: OK, no banned imports.
- PIHC3 build: `module_count: 529`, `artifact_count: 26892`, `diagnostic_count: 0`, `error_count: 0`, `blocked: false`.
- Copy-root shadows: 0.
- No-write SDK probe resolved all starter family shorthands without blocking: `idea`, `trait`, `event`, `focus`, `character`, and `technology`.

## Risks Or Blockers

- None for this slice.
- Families with multiple project-local templates still require the full template id, which is intentional to avoid guessing.

## Next

- Continue reducing end-user friction around template arguments and GUI create-module flows.
