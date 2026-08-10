# PIHC3 Rendered Authoring Hardening

Date: 2026-08-01

## Outcome

The real desktop authoring screen now accepts scalar project-template defaults
without crashing while it prepares AI planning context. Numeric and boolean
defaults/choices are normalized once for text controls and context summaries,
while malformed non-scalars remain ignored at the untrusted renderer boundary.

Retained create drafts also self-repair an empty historical `sourceRoot` from
the current project-template catalog. ParaDev preserves the user's object id
and form values, adopts the current default source root, and can continue the
preview/apply transaction instead of trapping the user in a permanently
blocked recovered draft.

The rendered PIHC3 Idea smoke fixture was brought forward to the current SDK
contracts: canonical project-browser schema/visibility, template source roots,
string-normalized scaffold results, explicit HeavenBase Catalog mutation
status, and nullable guided source forms.

## Physical project audit

- Exact path checked: `projects/PIHC3/src/modules`.
- 71 family directories contain 14,618 direct module folders.
- 90 direct collection folders remain under `src/collections`.
- Every direct module and collection folder uses `id - preferred-language
  title` and passes the browser-backed localization comparison.
- Physical `_component`, `_asset_component`, `legacy`, `inactive_modules`,
  symlink, empty, and malformed direct source directories: zero.
- The nested PIHC3 Git index still reports historical deletions with retired
  component/legacy path names. Those deletion records are absent from the
  working tree and are not discovery or compilation inputs.

## Rendered verification

The Vite/Tauri smoke opened the real localized PIHC3 Ideas workspace and
completed this flow:

1. Open the project-local `PIHC3 Basic Idea` template.
2. Enter `IDEA_RENDERED_FRIENDSHIP`, title, description, and numeric CIC.
3. Create the reviewed source draft.
4. Apply the draft.
5. Confirm one clean canonical row, three source files, enabled copy/module
   build/family build actions, and no renderer recovery screen.

Screenshots are under
`demos/.temp/authoring-audit-2026-08-01/01-renderer-crash.png` through
`05-pihc3-idea-applied.png`.

## Gates

- Desktop: 89 files and 1,454 tests passed.
- Strict TypeScript plus production Vite build passed.
- Python standard fast gate: 2,278 passed, nine native-Windows tests skipped,
  and 152 slow tests deselected by the repository profile.
- PIHC3 retired-layout and extensible-layout contracts passed.
- Clean/full and cached/full: 14,617 active modules, 106 collections, 35,131
  artifacts, zero diagnostics.
- Focus family partial: 738 modules, 28 collections, 12,499 artifacts, zero
  diagnostics.
- Focus module partial (`FOCUS_C01_C02_EVERFREE_FIELDTRIP`): 83 modules in its
  owning tree, one collection, 11,161 artifacts, zero diagnostics.
- Generated output contains no forbidden component, legacy, or inactive
  directory names.
