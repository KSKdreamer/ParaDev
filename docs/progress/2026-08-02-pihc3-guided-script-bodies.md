# PIHC3 Guided Script Bodies

This checkpoint removes the largest remaining Code-only authoring burden in
the cleaned PIHC3 tree while keeping source ownership in project-local
HeavenBase extensions.

## Outcome

- The generic PDX source-form contract now supports a Registry-declared
  `block-text` control and closed `replace-pdx-block-body` patch operation.
  Its exact UTF-16 span covers only the block interior; ParaDev continues to
  own the braces and surrounding source.
- Projection normalizes indentation for authors. Planning reparses the live
  source, resolves the declared path again, verifies its exact source and
  whitespace layout, validates the replacement as one PDX block interior,
  rejects stale or overlapping changes, and reparses the complete result.
- The desktop validates the same discriminated patch type and buffers the
  multiline editor until blur or Command/Ctrl+Enter. The SDK remains the
  write authority; React has no scripted-effect, scripted-trigger, on-action,
  or scripted-GUI branch.
- PIHC3's project-local Entity classes and Registry family providers now own
  the resource slots, compilation hooks, source-form hints, family creation,
  and scaffold fields for all four script-container families.
- Scripted Effect and Scripted Trigger use the reserved `$root` selector
  because 16 collision-preserving module folder ids intentionally differ from
  the source's keyed root block. On Action also uses `$root`, which covers
  empty hooks as well as hooks without a pre-existing `effect` block.
- Scripted GUI declares exact bodies for its `visible`, `triggers`, `effects`,
  and `properties` blocks through the same generic path contract.
- The create templates expose visible multiline body fields. Effect defaults
  to an empty body, Trigger to `always = yes`, On Action to an editable effect
  body, and Scripted GUI to editable effect, trigger, and property bodies.
  No visible metadata edit is required.

## Exact project audit

- All 8,593 live script-container modules projected successfully with at
  least one guided body control and zero failures.
- The audit produced 8,813 exact block-body controls: 8,289 across 8,279
  Scripted Effects, 87 across 87 Scripted Triggers, 116 across 116 On Actions,
  and 321 across 111 Scripted GUIs.
- The canonical `src/modules` and `src/collections` roots contain zero
  `_component`, `_asset_component`, `legacy`, or `inactive_modules`
  directories. The active layout remains one semantic folder per source unit.
- The audit and dry plans made no PIHC3 source changes.

## Rendered desktop proof

The current unsigned native app is
`apps/desktop/src-tauri/target/debug/bundle/macos/ParaDev.app`. It reopened the
cleaned PIHC3 project with 51 visible Registry families. Scripted Effects
loaded all 8,279 modules; `ADD_FOG_OF_WAR_BUILDING` displayed its live Effect
body in Guided mode. The New dialog displayed the project-owned multiline
Effect body and Title fields. Both checks were cancelled or left clean, so no
source draft was applied.

The app bundle completed successfully. The optional DMG layout step did not:
the normal release wrapper expected the separately packaged PIHC3 companion
archive, and the fallback invocation reached a noninteractive DMG-layout
limitation after producing the working `.app`. This is not a signed or
clean-machine release claim.

## Verification

- Focused Python block-body tests: 4 passed.
- Source-form, PIHC3 extensible-layout, and template-correctness set: 99
  passed.
- Focused desktop source-form/client set: 198 passed.
- Full desktop gate: 89 files and 1,462 tests passed.
- TypeScript and Vite production build passed; the existing large-chunk
  warning remains.
- Dry scaffold plans for all four changed templates produced one file each,
  with no write and no blocker.
- One module-partial dry build from each affected family completed with one
  selected module, 9,298 artifacts, and zero diagnostics.
- Targeted repository formatting, the core Heaven-style scan, YAML parsing,
  and `git diff --check` passed. The full dirty-worktree formatting command is
  currently red only on three unrelated pre-existing Doctrine files; none is
  part of this checkpoint.
