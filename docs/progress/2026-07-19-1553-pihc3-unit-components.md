# PIHC3 unit components: native ownership and deterministic regeneration

Date: 2026-07-19 15:53 +08

## Outcome

The complete PIHC3 `unit_component` family now has an explicit and testable ownership boundary:

- 24 path-preserving PIHC2 imports tagged `compiled-units`, with 147 records and 1,728 localization rows;
- one PIHC3-native unit-modifier registry, with six scalar registrations and 52 localization rows;
- six hand-maintained current-HOI4 compatibility modules, with 11 records and no module-owned localization rows.

Together the 31 modules contain 164 records and 1,780 localization rows. The PIHC changes are published on draft [HOI4-PIHC PR #2](https://github.com/Magolor/HOI4-PIHC/pull/2) at commit `cc234e287118eb8f4850d4c77dc4a00c9cc2c080`. ParaDev's portable contracts and pinned safety bridge remain on draft [ParaDev PR #4](https://github.com/Magolor/ParaDev-3/pull/4).

## Native modifier preservation

`UNIT_COMPONENT_UNITS_UNIT_MODIFIERS_UNIT_MODIFIERS` was still tagged as a generated PIHC2 module even though PIHC3 had intentionally rewritten it. A clean import would therefore replace the current six registrations with the 53-record PIHC2 registry, including 48 invalid vanilla-derived identifiers.

The module is now tagged `pihc3`, `native-unit-modifiers`, and `unit-support`. Its metadata describes the physical 378-byte, eight-line, six-record PDX file instead of the 2,982-byte legacy origin. Its source evidence separates that legacy origin from the native override. Localization was reduced from 530 stale rows to 52 coherent rows: the five inherited live keys remain translated in ten languages, while `modifier_army_sub_unit_infantry_magical_attack_factor` has accurate English and Simplified-Chinese text.

## Import safety and reproducibility

The importer now owns exactly the other 24 modules. It requires all declared sources, validates the expected `sub_units` or `equipments` wrapper and unique records, rejects unowned destination collisions, snapshots PDX and localization inputs before staging, validates the exact four-file module manifests and their semantics, and installs only through the shared rollback transaction. Generated PDX files end in exactly one newline under latest HeavenBase.

An independent checked-in localization contract covers all 24 paths, 192 declared source-owned keys, their exact language matrices, and all 1,728 rows without freezing translation values. This closes a reproduced failure in which every module retained at least one bilingual row but a truncated localization tree regenerated only 216 of 1,728 production rows. Contract schema/path/count drift, partial localization loss, blank values, and missing English or Simplified Chinese now fail before staging.

Source roots, the exact PDX paths, game/localization inputs, and the contract also reject symlinked intermediate ancestry. Missing inputs, contract failures, staging corruption, and `BaseException` interruption leave the existing destination unchanged. Clean replacement preserves the native modifier registry and all six current-HOI4 modules byte for byte.

## Portable evidence

ParaDev reconstructs all 24 legacy PDX files and their localization inputs from the committed PIHC3 modules. The fixture uses an explicit empty game root, regenerates all modules in deterministic order, and compares PDX/localization bytes, structural metadata/provenance, exact manifests, and canonical newlines. A dedicated native contract verifies the six current modifier identifiers, excludes all 48 removed identifiers, and checks the magical-attack localization.

The standalone PIHC corpus contract independently checks the 24 + 1 + 6 owner partition, the production localization manifest, physical metadata, native evidence, current-HOI4 compatibility set, and the full 147 + 6 + 11 record and 1,728 + 52 localization totals.

## Latest-HeavenBase test isolation

Latest HeavenBase now gives its global configuration context a persistent machine backend. ParaDev's tests already isolated `.paradev`, but a project build attempted to open the developer's real `~/.heavenbase/system.db` inside the sandbox. `tests/conftest.py` now eagerly binds `CM_HVNB` and `DEFAULT_CONTEXT` to a task-specific temporary root and in-memory backend. The subprocess config-migration test explicitly applies the same child-process bootstrap; it does not rewrite `HOME` or depend on user machine state.

## Verification

- PIHC script suites: 108 passed in 4.91 seconds.
- ParaDev unit-component/modifier contracts against the explicit PIHC worktree: 5 passed, 312 deselected.
- Production localization-contract coherence: 24 paths and 1,728 rows passed independently.
- Config/project isolation suites: 345 passed.
- The previously failing PIHC3 build node passed in 73.29 seconds with isolated HeavenBase state.
- Pinned ParaDev safety fixture: 2 passed and 1 expected skip; explicit live-fixture synchronization: 3 passed.
- Full standard ParaDev gate: 1,453 passed and 1 expected skip in 335.71 seconds.
- Black at 160 columns, Flake8, and both repository whitespace checks passed.
- The Heaven-style scanner reports only the accepted typed `pathlib` and pre-existing broad test-harness notices.
- Final independent review found no remaining P0 or P1. Its documentation-path P2 was corrected to use the local `dev` environment and an explicit ParaDev source path.

The historical fail-fast boundary now passes project-tree hygiene and all five unit-component/modifier checks, then stops at the first equipment-module importer test because its fixed PIHC2 resources directory is absent: six passed before that expected next-boundary failure.

## Next boundary

The next bounded checkpoint is the shared equipment-designer importer:

- 130 `equipment_module` modules: 50 plane and 80 tank;
- 49 `equipment_module_category` modules: 17 plane and 32 tank;
- 488 reconstructable legacy source files, 130 compiled `def.txt` records, and 179 committed DDS icons.

The committed definitions, metadata fields, category membership, and icons currently agree with the available PIHC_dev output. The importer itself is unsafe: its PIHC2 source root is absent, `--clean` deletes both families before validation, partial discovery succeeds silently, JSON and compiled-record coverage are not strict, missing DDS assets can be mislabeled or omitted, latest-HeavenBase newline behavior would drift all definitions, and no dedicated safety/corpus tests exist. The two families should therefore be hardened and migrated together before moving to `entity`.

Native Tauri visual acceptance remains blocked by the locked macOS session. No browser automation was used in this checkpoint.
