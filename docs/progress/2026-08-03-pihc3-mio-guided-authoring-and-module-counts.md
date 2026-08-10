# PIHC3 MIO Guided Authoring And Honest Module Counts

This checkpoint removes two sources of non-programmer confusion in the native
authoring workbench while keeping all HoI4 behavior behind the active Registry.

## Outcome

- The module-family footer no longer labels every family row as visible. It now
  distinguishes objects currently shown, Catalog objects already loaded, the
  complete family total, and family-wide source files. Filtered, paged, and
  filtered-plus-paged views each have explicit English and Chinese copy.
- The summary calculation lives in a small presentation model and the footer is
  a polite live status. React still receives family, source, and Catalog facts
  from the SDK; it does not infer HoI4 ownership.
- PIHC3's project-owned `military_industrial_organization` HeavenBase Entity
  extension now declares bilingual Guided-mode help for organization identity,
  inheritance, trait tokens, tree coordinates and anchors, parent policy,
  visibility and availability conditions, equipment and research scope, and
  organization/production/equipment bonus blocks.
- The generic PDX source-form projector consumes those declarations. The SDK,
  CLI, REST, MCP, and desktop therefore receive the same labels, descriptions,
  exact source spans, and guarded patch operations without a MIO switch in
  React or the generic SDK.

## Live Registry inventory

The supported environment resolves HeavenBase `0.1.2.1`. The active PIHC3
Registry contains 71 project extension families: 51 novice-visible families
and 20 hidden build-support families. All 51 visible families have at least one
authoring-ready project template; 53 templates are ready in total. Doctrine,
Focus, MIO, and Technology publish source-backed diagram providers through the
same Registry.

All seven live MIO PDX files project a Guided form. AI bonus weights, debug
organizations, and the three policy files fit completely. C01 and the large
generic organization file publish exact bounded coverage and retain Code mode
for the remainder instead of claiming complete form coverage.

## Verification

- Standard Python gate: 2,385 passed, 9 native-Windows-only skips.
- Complete PIHC3 extensibility contract: 32 passed.
- Real MIO family plan: 7 modules, 9,304 artifacts, zero diagnostics, not
  blocked.
- Focused desktop Guided-form/count/localization tests: 29 passed.
- Complete desktop gate: 90 files and 1,468 tests passed.
- TypeScript and Vite production build passed; the existing large-chunk
  advisory remains.
- PIHC3 source-layout preflight passed with no retired or malformed live source
  paths.
- Targeted Black, Ruff, and `git diff --check` passed.

This is an authoring-stability checkpoint, not a public release claim. Native
installer, Windows integration, and game-launch verification were intentionally
outside this user-prioritized slice.
