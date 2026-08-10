# 2026-06-08 17:39 Template-Backed GUI Families

## Scope

- Fixed a desktop GUI first-instance gap: families with SDK templates but no existing browser source rows now appear in the module list.
- Added a generic `projectModules` helper that derives module entries from both SDK browser families and SDK templates.
- Kept React form behavior generic: no HOI4-family-specific create-form logic was added.
- Updated the PIHC3 user manual and GUI spec to describe template-backed zero-row families.

## Behavior

- Existing browser families still drive counts and `ready` status when they have source rows.
- Known static modules switch from `planned` to `scaffold` when a template can create them.
- Template-only families such as `entity` and `state_lore` appear with generated labels and `scaffold` status.
- The existing module editor can then select the unambiguous project-local template and create the first source module through the SDK bridge.

## Verification

- Red first: `rtk npm --prefix apps/desktop exec vitest run src/projectModules.test.ts` failed because `./projectModules` did not exist.
- Green focused: `rtk npm --prefix apps/desktop exec vitest run src/projectModules.test.ts` passed with 2 tests.
- Desktop model tests: `rtk npm --prefix apps/desktop run test:model` passed with 13 tests after adding the new regression to the script.
- Desktop build: `rtk npm --prefix apps/desktop run build` passed.

## Unfinished Jobs

- Rendered Tauri verification for the SDK-backed create flow still needs a browser or desktop automation slice.
- Families with multiple template variants still need a template picker rather than the current unambiguous-template rule.
- GUI labels for many PIHC3-specific dynamic families are still SDK-derived English labels unless confirmed translations are added.
