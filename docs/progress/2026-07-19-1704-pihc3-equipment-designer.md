# PIHC3 equipment designer: portable corpus and atomic regeneration

Date: 2026-07-19 17:04 +08

## Outcome

The complete PIHC3 equipment-designer boundary is now portable, deterministic, and transaction-safe:

- 130 editable `equipment_module` records: 50 plane and 80 tank;
- 49 editable `equipment_module_category` records: 17 plane and 32 tank;
- one exact category partition covering all 130 modules without duplicates or orphans;
- 488 preserved PIHC2 evidence files and 179 compiled DDS icons;
- one checked production contract that rejects partial or internally malformed source trees before installation.

The PIHC changes are pushed to draft [HOI4-PIHC PR #2](https://github.com/Magolor/HOI4-PIHC/pull/2) at commit `5b609e9615c8272717830a006c8a89811e37f9a2`. ParaDev's portable contracts and pinned safety bridge remain on draft [ParaDev PR #4](https://github.com/Magolor/ParaDev-3/pull/4).

## Corpus contract

`scripts/data/pihc2_equipment_module_contract.yaml` is an independent strict-v1 inventory of all 179 source records. It pins plane/tank counts, exact category membership, source filenames, all 884 recursive `info.json` leaf paths, and the exact bilingual localization key matrix without freezing translation values. The file is 116,810 bytes and 3,648 lines with one trailing newline; its Heaven hash is `2b185fe24a7ee7eacd9d76eb7d8b5af4fe89f3741a32a5698242da178f83c475`.

The committed corpus has:

- 130 eight-file module manifests and 49 six-file category manifests;
- 130 one-record definitions totalling 40,904 bytes and 2,226 lines;
- 522 module localization rows and 98 category localization rows, all nonblank in English and Simplified Chinese;
- 179 DDS icons totalling 756,096 bytes, with 96 unique content hashes;
- 488 raw `default.png`, `info.json`, and `locs.txt` evidence files totalling 3,044,552 bytes.

All 179 provenance manifests now contain logical repository-relative paths only. No developer home directory, PIHC2 installation path, or compiled-mod root is embedded in generated modules.

## Localization repair

The raw `MODULE_TURRET_4A_SPHERE` evidence contains a historical bare English `[en.desc]` section while its Chinese row is correctly scoped. The raw file remains byte-identical. Generated `main.loc` narrowly normalizes that one row to `MODULE_TURRET_4A_SPHERE_desc`, and `legacy/source.yaml` declares the transformation. No global `desc` owner remains.

`MODULE_TURRET_3B_SPIN_desc_korean` remains intentional and is preserved in both languages. Two other Simplified-Chinese descriptions still repeat their English source text—`MODULE_CREW_2D_ENGINEER_desc` and `MODULE_SPECIAL_FUEL_TANK_LARGE_desc`—and remain translation-quality backlog rather than migration-integrity failures.

## Strict source semantics

The importer now validates the complete source tree and both compiled aggregates before staging. It requires the exact `equipment_modules = { ... }` wrapper, the correct DLC limit for plane or tank, unique `MODULE_*` records, assignment operators throughout every nested record, stable scalar domains, exact category linkage, and recursive agreement between `info.json` and compiled PDX. Duplicate JSON and YAML keys, unsafe path segments, missing or extra source entries, blank or incomplete localization, malformed section headers, symlinked ancestry, and missing or relabelled DDS data all fail preflight.

Independent adversarial review reproduced three subtle corruptions during development:

- Python considered JSON `true` equal to numeric PDX `1`;
- non-assignment PDX such as `xp_cost != 1` retained valid-looking keys and values;
- quoted PDX `"1"` or `"yes"` was collapsed into numeric or boolean metadata.

The final importer uses type-aware scalar decoding, bool-safe recursive comparison, and recursive key/operator validation. Regressions prove all three inputs are rejected without destination mutation.

## Dual-family transaction

All 130 modules and 49 categories are captured into one immutable prepared snapshot before staging rereads nothing. Both sibling destination families are collision-checked, staged on their destination filesystem, and validated against exact output bytes and manifests before installation. Every destructive rename and destination creation is journaled before it runs.

The installer moves both families' affected roots to one grouped recovery transaction before installing either family. `Exception`, `SystemExit`, and `KeyboardInterrupt` restore both prior trees, including their original existence state. If recovery itself fails, the importer raises `IncompleteMigrationRollbackError` and retains the transaction root containing both staged and backup state. `--clean` removes only roots carrying `compiled-equipment-modules` or `compiled-equipment-module-categories`; novice-authored and current-HOI4 roots remain untouched.

## Portable acceptance

ParaDev reconstructs a complete temporary PIHC2 resources tree, two DLC-wrapped compiled aggregates, and all 179 DDS inputs solely from committed PIHC3 evidence. It regenerates the full 130 + 49 set into temporary sibling destinations and checks exact definitions, localization, icons, raw evidence, structural metadata, portable provenance, category membership, owner-scoped clean behavior, and canonical newlines. It does not use Steam, a personal mod installation, or the user's original PIHC3 checkout.

ParaDev's default importer-safety gate now pins the production importer, contract, and synthetic safety suite to PIHC commit `5b609e9615c8272717830a006c8a89811e37f9a2`. The fixture remains text-only; it does not duplicate the multi-megabyte equipment-designer corpus.

## Verification

- Full PIHC script suites: 165 passed in 7.67 seconds.
- Focused equipment-designer safety and standalone corpus: 57 passed.
- ParaDev portable equipment-module contracts against the explicit PIHC worktree: 3 passed, 314 deselected.
- Pinned ParaDev safety fixture: 2 passed and 1 expected skip; explicit live-fixture synchronization: 3 passed.
- Full standard ParaDev gate: 1,453 passed and 1 expected skip in 479.72 seconds.
- Black at 160 columns, Flake8, and both repository whitespace checks passed.
- Final independent review found no remaining P0, P1, or P2 finding.
- The Heaven-style scanner reports accepted typed-`pathlib` and pre-existing broad test-harness notices, plus one documented direct-PyYAML exception: HeavenBase's YAML helper has no duplicate-key rejection surface, so the strict production contract uses a safe custom loader only for that check.

A concurrent review invocation produced two ignored bytecode files under `scripts/__pycache__`. The directory was moved intact to `/private/tmp/pihc3-equipment-cache-quarantine.WQyb1P`; the dedicated project-tree hygiene node then passed, and no generated cache remains in the PIHC worktree.

The historical migration boundary now passes the entity-family slot contract and stops at the next personal-root entity importer test because its obsolete PIHC2 resources path yields zero model directories: one entity test passed before that expected next-boundary failure.

## Next boundary

The next checkpoint is the aggregate `entity` bundle. Its 182 checked-in artifacts are already byte-identical to the available compiled baseline, and clean PIHC2/HOI4DEV source repositories are available locally without Steam. The importer is currently destructive, partial-input tolerant, non-portable, and non-transactional.

The same checkpoint must also repair a novice-facing starter defect: `pihc3:entity/basic` currently writes `mesh.gfx` and `entity.asset` at module root, while the family only accepts `gfx/models/**`. A newly created entity therefore has no required PDX source and cannot build. Entity work will keep the existing 42.8 MB aggregate byte-stable, add a production/corpus contract and portable fixture, harden owner-scoped regeneration, and prove that a template-created entity loads and emits its documented paths.

Native Tauri visual acceptance remains blocked by the locked macOS session. No browser automation was used in this checkpoint.
