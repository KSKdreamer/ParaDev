# PIHC3 deterministic parity checkpoint

## Outcome

PIHC3 now has an isolated, portable build branch that no longer depends on one developer's compiled `PIHC_dev` directory. A complete build from committed modules succeeds against the current ParaDev and local HeavenBase source, localization postprocessing is repeatable and source-map-owned, five C08 idea migrations match the available PIHC2 evidence, and Sombra's one semantic trait repair is editable through canonical metadata.

The work is published as draft [HOI4-PIHC PR #2](https://github.com/Magolor/HOI4-PIHC/pull/2), based on `origin/v3.1`. The user's original dirty PIHC3 checkout was not modified.

## Build and localization changes

- Removed the 455-line absolute `copy_roots: pihc_dev` block after confirming that it owned zero emitted artifacts. PIHC3 output is now derived from checked-in modules and collections.
- Added `PARADEV_ROOT` support to `compile.bash` so an isolated PIHC3 worktree can build with the current ParaDev/HeavenBase environment.
- Made localization winner selection consume the complete `paradev.build.source-map.v1` manifest. Native feature owners outrank the migrated `localization_component` baseline; emitted path and source order provide stable tie breaks.
- Added `localisation-postprocess.json` state so repeat builds restore and recreate only postprocessor-owned replacement files before deduplication.
- Validated all stored postprocess paths canonically beneath the selected output and `localisation/replace` roots. Traversal entries, bare directories, and symlink escapes are rejected before deletion.
- Artifact-emitting `--family`, `--module`, and `--collection` requests are promoted to a full project build because localization ownership is project-wide. `--plan-only` retains fast target-scoped validation.
- Updated parity reviewers to load the selected project through `Project.load`, resolve current project roots, require an explicit compiled baseline, and execute repeated `--only` selectors safely.

## Entity parity repairs

Five idea modules now preserve the reviewed current PIHC2/compiled localization semantics in both editable `main.loc` and module-local legacy evidence:

- `IDEA_C08_FADED_FRIENDSHIP_1`
- `IDEA_C08_FADED_FRIENDSHIP_2`
- `IDEA_C08_FADED_FRIENDSHIP_3`
- `IDEA_C08_FADED_FRIENDSHIP_4`
- `IDEA_C08_NEVER_FORGET`

The Sombra trait importer now maps the legacy pseudo-comment key `// infantry_magical_attack_factor` to `modifier_army_sub_unit_infantry_magical_attack_factor`. The canonical `0.35` value is mirrored through the module body, `trait_keys`, `direct_scalar_fields`, and `modifier_fields`; `legacy/info.json` and `info_keys` retain the source spelling as provenance.

## Real PIHC3 acceptance

Acceptance used a copy-on-write PIHC3 fixture and isolated output under `/private/tmp`; it did not mutate the original project checkout or the user's live launcher mod.

| Check | Result |
| --- | --- |
| Full build | 18,038 modules; 78 collections; 37,553 emitted artifacts |
| Diagnostics | 0 diagnostics; 0 errors; unblocked |
| Strict-metadata build | 0 diagnostics |
| Source ownership | 0 copy-root owners; 1,763 `localization_component` baseline owners |
| Localization postprocess | 6,073 duplicate keys; 6,088 removed entries; 1,672 changed files; 3,338 vanilla-reference moves |
| Repeated output | 37,552 files; 1,247,915,801 bytes; no added, removed, or content-changed paths |
| Component-sorted tree SHA-256 | `523c55274f6cc0346103b0d75cf0a4453b945f9677cdd3f4d534f269462e63a8` |
| Per-file manifest SHA-256 | `d3a4d349f97ffdc76863c49d497dc0cf0baf4f086869b863864051c7067f76e3` |
| Startup error contracts | passed |

The five repaired ideas and Sombra each pass a target-scoped dry build with one module, five artifacts, and zero diagnostics. An actual artifact-emitting request for one idea produced the documented promotion warning, completed the full build, and repeated the same postprocess counts.

The hash audit exposed an important reporting rule: a tree digest is meaningful only with a declared path-order contract. Python `Path` component ordering and globally sorted relative-path strings produce different aggregate digests over the same byte-identical per-file manifest. The acceptance claim therefore uses the original component-sorted contract and also records the independently comparable per-file manifest digest.

## Portable ParaDev contract harness

`tests/test_pihc3_migration_contracts.py` now accepts `PARADEV_PIHC3_ROOT`, allowing it to validate the clean branch rather than an ignored workspace snapshot. New contracts cover the build wrapper, complete source-map ownership, absence of external copy roots, deduper safety/idempotence, reviewer CLIs with `--only`, the five C08 localizations, and the Sombra importer/runtime shape.

The trait importer tests no longer require a deleted `~/Documents/.../PIHC2` resource tree. They reconstruct PIHC2-shaped inputs from the committed module-local `legacy/info.json` and `legacy/locs.txt` evidence, then assert that the current importer reproduces editable metadata.

Verification for the updated harness:

- 316 tests collect against the clean PIHC3 worktree;
- 11 focused build, dedupe, reviewer, localization, trait, and startup contracts pass;
- both portable trait-import round trips pass;
- Black, Flake8, and `git diff --check` pass.

The earlier attempt to run the complete historical 316-test file was stopped after it exposed numerous stale clean-versus-dirty snapshot expectations. This report does not claim that historical suite is green. The next parity block must reconcile those assertions one domain at a time against the clean `v3.1`-based branch instead of preserving machine-local or dirty-snapshot assumptions.

## Repository state and remaining work

The PIHC3 branch contains four reviewable commits:

1. `b3b9fee84` — deterministic build and source-map localization ownership;
2. `812e51160` — five C08 localization repairs;
3. `8d780a735` — canonical Sombra trait mapping;
4. `7bec9b936` — safe targeted-build promotion and state-path containment.

The original PIHC3 checkout remains at `7a4efe41bf07084ffe8fe56c2ba2f158ea14527f` with its pre-existing modified and untracked migration work intact. That dirty delta is evidence for subsequent entity-domain ports, not content to mix into this deterministic build PR.

Native Tauri visual acceptance and final packaging remain blocked by the locked macOS GUI session. The next work continues with historical-contract reconciliation and the next remaining entity migration slice, while retaining the current source-independent Python, desktop, Rust, bridge, and real-build gates.
