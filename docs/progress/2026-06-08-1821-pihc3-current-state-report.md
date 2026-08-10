# 2026-06-08 18:21 PIHC3 Current-State Report

Linear: TAL-298, TAL-297

## Done

- Rechecked the PIHC3 creation surface after the packaged Tauri smoke.
- Updated the user manual with a current command for inspecting template support and the compact primary-field policy.
- Refreshed `projects/PIHC3/docs/migration/00-design.md` so developer-facing migration guidance distinguishes native imported content from template-backed creation support.

## Evidence

- `rtk uv run paradev templates projects/PIHC3 --json`: 45 templates across 44 families.
- Current template payloads keep primary fields compact: either `title` or `title` plus `description`; other knobs are advanced/defaulted.
- `rtk uv run paradev summary projects/PIHC3 --json`: 529 modules, 26,892 artifacts, 0 diagnostics, 0 errors, `blocked: false`.
- Native imported modules remain concentrated in two families: `idea` and `trait`.

## Result

The SDK/CLI/GUI creation surface is broad enough for normal authoring experiments, including the user-named families `idea`, `focus`, `event`, `character`, `trait`, and `technology`.

The overall PIHC2-to-PIHC3 migration is still not complete. Most non-idea/non-trait families have starter templates and migration notes, not imported and parity-reviewed legacy inventories.

## Next

- Continue turning scaffold-only families into imported native content.
- Add parity validators for aggregate-heavy families such as events, focuses, inventory items, superevents, state lore, entities, scripted GUI, and generated assets.
- Keep copy-overlay exclusions, user docs, migration notes, and Linear aligned as each family reaches parity.
