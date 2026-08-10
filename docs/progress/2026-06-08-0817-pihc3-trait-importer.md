# PIHC3 Trait Importer Progress

Date: 2026-06-08 08:17 CST

Linear: TAL-297

## Done

- Replaced `projects/PIHC3/scripts/migrate_pihc2_traits.py` so it imports PIHC2 traits into canonical `src/modules/trait/TRAIT_<TAG>/` modules.
- Removed the obsolete `ahvn` dependency and old `src/traits` destination.
- Preserved HOI4DEV trait defaults: `leader_traits`, `random = no`, and `ai_will_do = { factor = 1 }`.
- Converted legacy `[language.key]` trait localization into YAML-backed `main.loc`.
- Added focused SDK/example coverage for one fake PIHC2 trait import and verified the generated module builds through the current routed trait family.
- Updated `projects/PIHC3/docs/migration/04-traits.md`.

## Verification

- `rtk bash scripts/test.bash tests/test_sdk_examples.py::test_pihc3_trait_importer_writes_current_module_layout -q`
- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q`
- `rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py projects/PIHC3/scripts/migrate_pihc2_traits.py`
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_traits.py --resources-root <temp-resources> --dest-root <temp-dest> --only ARCHAEOLOGIST`
- `rtk uv run paradev summary projects/PIHC3 --json`

## Risks Or Blockers

- The importer currently maps all legacy PIHC2 traits to `settings.subtype: country_leader`, matching HOI4DEV `AddTrait(...)`. Unit-leader and scientist trait routes need a later schema decision before import.
- Existing parent-repo desktop and SDK edits remain in the worktree from prior work and were not reverted.

## Next

- Run the trait importer on a controlled PIHC3 branch or add a parity report before replacing the copied legacy trait outputs at scale.
