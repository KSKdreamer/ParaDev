# PIHC3 equipment transaction and portable parity

Date: 2026-07-19 14:36 +08

## Outcome

The complete regular-equipment boundary is now portable, transaction-safe, and reproducible against committed PIHC3 evidence. All 167 equipment modules (34 archetypes and 133 equipment records) regenerate with byte-identical `def.txt`, `main.loc`, copied UI assets, and PIHC2 resource evidence. Metadata and source manifests also match structurally after excluding only the original compiled-source byte widths that cannot be reconstructed from normalized PDX indentation; their paths, line counts, record/localization facts, assets, and semantic settings remain exact.

The PIHC changes are published on draft [HOI4-PIHC PR #2](https://github.com/Magolor/HOI4-PIHC/pull/2) at commit `435d26ed130082b32fca2452132b157ad83e1fb1`. ParaDev's portable contract and pinned safety bridge remain on draft [ParaDev PR #4](https://github.com/Magolor/ParaDev-3/pull/4).

## Import safety

The previous importer could delete the whole equipment family before validating either source root. On this machine the old default PIHC2 resource path is absent, so the documented `--clean` path would have erased all 167 modules and reported a successful zero-module import.

The importer now:

- requires explicit compiled-mod and PIHC2 resource roots;
- validates exact resource/compiled ID coverage, duplicate and malformed PDX records, real source files, mapping-shaped `info.json`, and nonempty English/Simplified-Chinese primary localization;
- preserves only PDX-referenced auxiliary tooltip localization, assigns shared rows to the first source owner in deterministic import order, rejects conflicting values, and requires both supported languages;
- validates the observed asset layouts, including asset and source symlink ancestry;
- stages the full snapshot on the destination filesystem, validates its exact file manifest and semantic identity, and installs only through the shared rollback transaction;
- rejects unowned or symlinked collisions and removes stale modules only when they carry the importer-specific `compiled-equipment` tag;
- uses latest-HeavenBase copy/serialization helpers, writes exactly one final newline, supports custom source-root provenance, and omits the obsolete raw `object_id` metadata key.

The 167 committed module metadata files now carry the owner tag. The three curated tooltip owners retain all six shared keys across both languages, and their localization manifests are reconciled. The Catapult localization byte count is also reconciled with its physical source.

## Portable evidence

The deterministic fixture reconstructs all required inputs from committed modules instead of personal mod or Steam paths:

- 35 compiled equipment PDX files: 34 one-record archetype files plus the 133-record aggregate;
- 337 compiled UI assets totaling 6,309,288 bytes;
- 465 PIHC2 resource-evidence files;
- 167 localized folder identities and source manifests.

The corpus contract additionally verifies 158,227 equipment-definition bytes across 7,539 lines and 117,113 localization bytes across 2,797 lines. All metadata titles equal their nonempty English object rows, and every committed localization key has an English and Simplified-Chinese owner.

## Verification

- PIHC nested script suites: 76 passed in 2.96 seconds.
- ParaDev equipment family/importer contracts against the explicit PIHC worktree: 4 passed, 312 deselected in 13.61 seconds.
- Pinned ParaDev safety fixture: 2 passed and 1 expected skip; explicit live-fixture synchronization: 3 passed.
- Full standard ParaDev gate: 1,453 passed and 1 expected skip in 375.29 seconds.
- Black at 160 columns, Flake8, and both repository whitespace checks passed.
- The Heaven-style scanner reports only the accepted typed `pathlib` notices in the importer and its two tests.
- Independent review found no P0 issue. Its bilingual-auxiliary-localization and strict-`info.json` findings were fixed and covered before commit.

The original user checkout remains at `7a4efe41bf07084ffe8fe56c2ba2f158ea14527f` and was not edited; its existing dirty changes remain user-owned.

## Remaining observations

The mutable local PIHC_dev tree is not used as the image oracle: its 169 DDS payloads currently differ from the committed assets at the same sizes, while its 141 GFX and 27 GUI files agree. Refreshing art should therefore be a deliberate visual-review change, not an incidental migration side effect.

Novice-facing equipment content still has a separate quality backlog: 72 modules retain `TODO` descriptions and nine inherited English titles spell `Chassis` as `Chasis`. Those strings were not changed in this parity/safety checkpoint.

The next historical boundary is unit support. A read-only audit found that one module still tagged `compiled-units` is actually an intentional PIHC3-native six-record rewrite; the legacy importer would overwrite it with 53 registrations, including 48 invalid vanilla identifiers. That module should be reclassified and reconciled before the remaining 24 legacy unit components receive the same portable transaction contract.

Native Tauri visual acceptance remains blocked by the locked macOS session. No browser automation was used in this checkpoint.
