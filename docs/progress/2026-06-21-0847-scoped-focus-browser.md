# Scoped Focus Browser Progress

Date: 2026-06-21 08:47

Linear: TAL-000

## Done

- Added family/module/collection filters to source discovery so scoped browser requests can avoid parsing unrelated PIHC3 modules.
- Routed `Project.browser(...)` through a private scoped dry-build path when browser filters are present, while leaving unfiltered SDK build/summary behavior unchanged.
- Normalized family-scoped browser module shorthand such as `--family focus_tree --module C01_MAIN` to `focus_tree/C01_MAIN`.
- Added a regression test proving a `focus_tree/C01_MAIN` browser request does not load an unrelated family module.

## Verification

- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/build/discovery.py src/paradev/sdk/project.py tests/test_project.py`
- `rtk uv run pytest tests/test_project.py tests/test_pihc3_migration_contracts.py::test_pihc3_focus_tree_preview_icons_resolve_to_migrated_components`
- `rtk uv run paradev project-browser projects/PIHC3 --family focus_tree --module C01_MAIN --json` returned in about 4.7 seconds with one `module:focus_tree/C01_MAIN` item.

## Risks Or Blockers

- Full unfiltered PIHC3 browser loads still need separate attention; this slice optimizes the common focus-tree editor scoped load path.

## Next

- Thread the scoped browser call through any remaining desktop entry points that still request whole-project browser payloads before opening a single focus-tree diagram.
