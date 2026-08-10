# 2026-06-08 17:56 PIHC3 Coverage Audit

## Scope

- Audited whether PIHC3 is ready for cleanup/goal-complete treatment after the template-backed SDK and GUI work.
- Separated creation-surface coverage from full legacy-content migration coverage.
- Synced the user manual and Linear plan wording with the current SDK/CLI/GUI surface.

## Evidence

- `Project.load("projects/PIHC3").templates()` lists 45 templates total.
- PIHC3 has 44 project-local template families:
  `achievement`, `autonomous_state`, `balance_of_power`, `bookmark`, `building`, `character`, `continuous_focus`, `country`, `decision`, `difficulty_setting`, `division`, `doctrine`, `entity`, `equipment`, `event`, `faction`, `focus`, `game_rule`, `idea`, `idea_category`, `ideology`, `intelligence_agency`, `inventory_item`, `modifier`, `on_action`, `operation`, `operation_phase`, `operation_token`, `operative_codename`, `opinion_modifier`, `resistance_activity`, `resource`, `scripted_effect`, `scripted_gui`, `scripted_trigger`, `special_project`, `state`, `state_lore`, `strategic_region`, `superevent`, `technology`, `trait`, `unit_medal`, and `wargoal`.
- Native imported modules under `projects/PIHC3/src/modules` currently total 529 modules across 2 families:
  - `idea`: 390
  - `trait`: 139
- `rtk uv run paradev build projects/PIHC3 --emit-manifests --json` completed with:
  - `module_count`: 529
  - `artifact_count`: 26892
  - `diagnostic_count`: 0
  - `error_count`: 0
  - `blocked`: false
- The build emitted expected manifest files under `projects/PIHC3/.paradev/build`: `artifacts.json`, `assets.json`, `collections.json`, `dependencies.json`, `diagnostics.json`, `localization.json`, `modules.json`, `source-map.json`, `sprites.json`, and `summary.json`.
- Dry-run `Project.create_module(..., write=False)` probes for `idea`, `focus`, `event`, `character`, `trait`, and `technology` all returned unblocked plans and wrote no files.

## Conclusion

PIHC3 is broad enough for normal end-user creation experiments through the SDK and GUI: the user-named module examples (`idea`, `focus`, `event`, `character`, `trait`, and `technology`) have project-local templates, compact primary fields, defaulted advanced fields, and unblocked dry-run scaffold plans.

The overall PIHC2-to-PIHC3 migration is not complete enough to mark the long-running goal complete. The build is stable, but actual native imported legacy content is still concentrated in ideas and country-leader traits. The other 42 project-local template families are creation scaffolds plus migration notes, not proven full legacy inventories.

## Unfinished Jobs

- Import and review real legacy content for non-idea and non-trait families, especially focuses, events, characters, technologies, decisions, achievements, inventory items, superevents, state lore, entities, and country/state/map families.
- Verify rendered Tauri GUI create/apply behavior against the SDK bridge. The Vite and model/build checks pass, but the browser MCP profile was locked during the last rendered smoke attempt.
- Add parity validators where the template produces only an inert starter shell and PIHC2 had aggregation, generated assets, GUI/scripted-localisation wiring, or multi-language output.
- Keep the copy-overlay exclusions aligned as each native family reaches parity, so generated native artifacts do not silently shadow legacy artifacts.
- Continue updating `docs/user-manual/pihc3.md` and `projects/PIHC3/docs/migration/` when a family moves from scaffold-only to imported-and-reviewed.
