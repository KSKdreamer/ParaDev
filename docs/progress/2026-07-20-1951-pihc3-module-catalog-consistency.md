# PIHC3 module catalog consistency audit

Date: 2026-07-20 19:51 +08

## Outcome

The second-pass audit confirms that the cleaned PIHC3 module sidebar is complete
and internally consistent. The project has 89 real source families: 47
author-facing families and 42 path-preserving support families. Normal ParaDev
navigation shows exactly the 47 author-facing families in both English and
Chinese. The support families stay build-active but are hidden by explicit
project metadata, and the four former frontend placeholders are absent.

The original mixed-language list was not evidence of two independently loaded
PIHC3 projects. It combined localized authoring families, English fallback names
for real child/support families, and four static rows that did not exist in the
project. The first cleanup corrected that boundary. This pass adds exact
cross-repository contracts so a count-preserving family substitution, stale
alias, missing translation, or phantom row cannot silently restore the problem.

## True project inventory

| Inventory group | Count | Navigation | Build |
| --- | ---: | --- | --- |
| Template-backed authoring families | 44 | Visible and localized | Active |
| Real child-domain families | 3 | Visible and localized | Active |
| Path-preserving support families | 42 | Hidden by `visible: false` | Active |
| Frontend-only placeholders | 4 | Absent | Not project families |

The child-domain families are `equipment_module`,
`equipment_module_category`, and `special_project_reward`. The removed phantom
rows are `assets`, `localization`, `map`, and `music`.

The 42 support families are not deletable legacy duplicates. Every one owns
current output, and together they own 13,156 required artifacts. The current
artifact manifest contains 37,556 unique targets and no multi-owner collision.
Deleting those sources would remove about 35% of the compiled mod rather than
cleaning duplicate navigation rows.

## Source and rebuild verification

The selected disposable workspace remained:

`/Users/magolor/Projects/ParaDev/PIHC3-GUI-Smoke`

Before and after the rebuild, its `src/modules` tree contained 81,263 files and
was byte-identical to the canonical PIHC3 worktree. The build did not change the
selected source or worktree state. The protected checkout under
`ParaDev-3/projects/PIHC3` was not modified.

The fresh full build completed with:

- 18,175 modules;
- 78 collections;
- 37,556 artifacts;
- zero diagnostics and zero errors;
- `blocked: false`.

All 37,556 declared artifact paths exist: 37,555 output-root files plus the
build-root launcher. The 12-file build-manifest tree was regenerated
successfully.

## Packaged GUI verification

The exact packaged macOS application was inspected in both locales. The Chinese
accessibility tree reported `模块 47`; the English tree reported `Modules 47`.
All 47 labels were localized without English fallback in Chinese or Chinese
fallback in English. Neither locale contained a support-component row or one of
the four phantom rows. The app was returned to Chinese with no open workspace
tabs after the check.

## Durable regressions

PIHC3 now owns an exact inventory contract that pins:

- the 47 visible-family allowlist;
- the 42 hidden-family allowlist;
- the ten registry-owned families not declared as custom manifest families;
- equality between the physical module roots and SDK browser inventory;
- exact 89/47/42 totals.

ParaDev now owns the presentation-side contract. It maps all 47 raw family names
to their canonical module IDs, requires distinct non-empty English and Chinese
labels, requires exactly 47 project-backed rows, and rejects the four phantom
rows. Existing tests continue to prove that hidden aliases and templates cannot
leak back into normal navigation.

## Verification

- Focused desktop module/application tests: 71 passed.
- Full desktop frontend: 62 files and 1,134 tests passed.
- TypeScript typecheck and production Vite build: passed; only the existing
  large-chunk advisory remains.
- Focused SDK visibility contracts: 3 passed.
- PIHC3 exact family-inventory contract: passed.
- PIHC3 project-local script suite: 257 passed.
- PIHC3 inventory test Ruff and Heaven-style scans: passed.
- ParaDev repository formatting: 162 files unchanged.
- Both repositories: `git diff --check` passed.

## Independent historical-contract diagnostic

An additional serial run used an exact clean archive of canonical PIHC3 commit
`6441e2d23`, with Git metadata and all generated caches/build outputs excluded.
It completed 176 of 320 ParaDev migration-contract tests in about 31 minutes
before being stopped at the explicit partial boundary: 165 passed and 11 failed.
The family visibility/navigation contract passed, including its 89/47/42
assertions.

The 11 observed failures are outside module navigation: two cover current
manifest/script-layout drift, while nine cover legacy importer source/metadata
parity for Division, Modifier, Opinion Modifier, Country, Country Component,
and Common Component. This partial diagnostic is not presented as a complete
suite result; it records a separate future migration-contract cleanup queue.

## Boundary

The novice sidebar is now deliberately a domain-authoring surface, not a dump of
the complete build registry. Hidden support families remain available through
SDK/browser payloads, diagnostics, and builds until a dedicated Advanced/Build
Support editor is introduced.
