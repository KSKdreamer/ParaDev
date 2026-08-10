# PIHC3 portable inventory and historical-entity checkpoint

## Outcome

PIHC3's 80 migrated inventory items are now readable and safely regenerable with current HeavenBase. Every generic-editor title matches the committed English item localization, generated localization has exactly one terminal newline under the latest `save_txt` contract, and PIHC2 inventory regeneration is a validated same-filesystem transaction rather than a destructive folder rewrite.

The historical migration contracts for inventory items, superevents, and all 79 state-lore modules no longer read the author's personal PIHC2 or PIHC_dev folders. They reconstruct temporary legacy-shaped inputs from committed PIHC3 evidence and require deterministic round-trip parity. The next fail-fast boundary is the equipment importer, whose old monolithic inputs still need a portable reconstruction.

The PIHC changes are published in draft [HOI4-PIHC PR #2](https://github.com/Magolor/HOI4-PIHC/pull/2) at commit `199a388c7c20ffc0ce4e96b2365d883af0a48ac1`. ParaDev's corresponding contracts and pinned private-repository fixture remain on draft [ParaDev PR #4](https://github.com/Magolor/ParaDev-3/pull/4).

## Novice-readable inventory modules

The importer previously canonicalized `en` to `l_english` before asking a title helper that recognized only legacy language identifiers. All 80 modules consequently exposed folder-derived titles such as `5Lg Artifact Staff Of Sacanas` in the generic GUI. The shared helper now accepts both legacy and canonical English/Simplified-Chinese identifiers, and every module metadata title is checked against its own committed English item row. The representative item is now `Staff of Sacanas`.

All imported inventory modules carry the dedicated `compiled-inventory-items` owner tag. The generic `pihc2` provenance tag and `inventory-items` domain tag are intentionally not ownership signals, so a novice-created module using either tag is preserved by clean regeneration.

Current HeavenBase appends one newline in `save_txt`. The shared migration writers now strip their rendered terminal newline before saving, and focused byte contracts prove copied and generated `.loc` files end with exactly one newline rather than two.

## Transactional PIHC2 inventory regeneration

Before any destination rename, the importer now validates:

- a real source root, nonempty selection, unique item tags, and requested-tag coverage;
- each legacy `locs.txt` and `small.png`, plus a mapping-shaped optional `info.json`;
- compiled effect and trigger files with the current item's `ADD_..._1`, `DEL_..._1`, and `TRIGGER_HAVE_..._1` identities;
- both expected DDS icons;
- English and Simplified-Chinese compiled localization containing a nonempty row for the current item key.

Effects and triggers are copied into staged snapshots before metadata is derived. Each staged module must then match its exact required file manifest and semantic PDX identities before installation. This closes the race where a validated source could disappear or be replaced with unrelated-but-parseable content before the old destination was touched.

Installation uses the shared transaction engine:

- staging is created beside the destination on the same filesystem;
- symlinked ancestry, symlinked module roots, and unowned same-ID collisions are rejected;
- `--clean` removes only `compiled-inventory-items` modules and is rejected when combined with `--only` or `--limit`;
- every destructive rename is pre-registered, and `BaseException` failures restore the previous tree;
- incomplete rollback keeps transaction evidence and reports its recovery path.

The focused suite covers normal scoped clean, generic-tag preservation, selective-clean rejection, duplicate tags beyond a limit, missing and semantically wrong sources, staging failure, symlink/unowned collisions, `KeyboardInterrupt` rollback, and incomplete rollback preservation. Independent final review found no remaining P0-P2 issue.

## Portable historical fixtures

Inventory item `5LG_ARTIFACT_STAFF_OF_SACANAS` is reconstructed from its committed legacy files, effect, trigger, icons, and normalized localization. The importer must reproduce metadata, every emitted artifact, every legacy byte, and every portable provenance field exactly; only fixture-root absolute paths are normalized.

Superevent fixtures build distinct synthetic `SUPER.txt` and `SUPER_NEWS.txt` aggregates from committed events 1 and 2. Event 2 is a real decoy, so event 1's exact definition round trip proves both aggregate-file selection and event-ID filtering rather than passing vacuously. Metadata, definition, localization, DDS pictures, legacy PNG/JSON/text files, and portable provenance all match module 1.

State lore reconstructs all 79 original source directories from committed relative provenance and legacy bytes. It emits the two compiled aggregates through the current `StateLoreFamily`, verifies exact state-ID membership and order, and round-trips `STATE_LORE_217` byte for byte across PDX, localization, and legacy evidence. Only the original absolute source root and two compiled-file paths are inherently nonportable.

These fixtures prove deterministic consistency against committed PIHC3 evidence. They cannot recreate uncommitted historical aggregate comments/formatting, original PNG-to-DDS encoder provenance, or the unavailable absolute PIHC2 checkout.

## Verification

| Check | Result |
| --- | --- |
| PIHC script suite | 51 passed in 1.17 seconds |
| Focused ParaDev inventory/superevent/state-lore contracts | 9 passed; 307 deselected |
| Historical contract prefix through state lore | 23 passed before cache quarantine; remaining 18 passed afterward |
| Full project-build contract inside that prefix | passed against current PIHC3 and local HeavenBase |
| Pinned importer-safety fixture | 2 passed; live-sync comparison skipped by design |
| Explicit live PIHC importer-safety gate | 3 passed with every pinned file byte-identical |
| ParaDev standard gate | 1,453 passed; 1 skipped; 2 warnings in 8 minutes 35 seconds |
| Black, Flake8, and `git diff --check` | passed |
| Independent safety review | no remaining P0-P2 findings |

The Heaven-style scanner's only notices on the four touched PIHC Python files are their intentional typed `pathlib` imports. The standard ParaDev fixture now pins both real PIHC safety suites plus their three production importers at immutable PIHC commit `199a388c7c20ffc0ce4e96b2365d883af0a48ac1`.

One historical test deliberately detected bytecode caches produced by a concurrent nested run. Those generated directories were moved intact to `/private/tmp/pihc3-pycache-quarantine-20260719-inventory`; the clean cache contract then passed, and no cache artifact remains in the PIHC worktree.

## Next boundary

The first remaining historical failure is equipment. Three equipment-family contracts pass before `compiled_equipment_sources()` finds zero of the expected 167 definitions because the personal PIHC_dev aggregate is absent. The committed equipment modules preserve definitions, localization, assets, and legacy source evidence, so the next block will reconstruct a semantic aggregate fixture from those modules and separate functional importer assertions from irreconstructable monolithic-file provenance.

The historical contract file still contains 39 direct PIHC2-resource references, 158 PIHC_dev references, and 9 mutable Steam game-root references. Unit components, equipment modules/categories, entity/model bundles, and current-game snapshots remain systematic portability slices after equipment. Native Tauri visual QA and final packaging also remain blocked by the locked macOS GUI session.
