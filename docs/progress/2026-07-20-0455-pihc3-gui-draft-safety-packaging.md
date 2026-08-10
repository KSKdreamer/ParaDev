# PIHC3 GUI draft safety and verified package

Date: 2026-07-20 04:55 +08

## Outcome

ParaDev now rejects malformed JSON/YAML, non-standard JSON numeric constants, over-limit UTF-8 text, parser recursion, and PIHC3-invalid Entity record or assignment drafts before changing any source file. The desktop keeps a rejected draft editable, announces the error as an accessibility alert, gives `.yaml` and `.yml` files the YAML language extension instead of the PDX service, and refreshes project/build diagnostics after a successful source-text Apply.

The PIHC3 Entity family owns its domain validation through the optional `validate_source_text` family hook. `record.json` uses the existing strict duplicate-free portable-record validator and `legacy/entities.json` uses the existing ordered assignment validator. ParaDev remains domain-neutral and batch-preflights every text edit before its first filesystem mutation.

The changes are pushed to the existing draft-PR branches:

- PIHC3 `8cc1bf65f` (`feat(entities): validate GUI drafts before write`), draft PR #2;
- ParaDev `d1bb7c3d` (`fix(editor): validate structured drafts before write`), draft PR #4.

## Packaged GUI investigation

The user selected `/Users/magolor/Projects/ParaDev/PIHC3-GUI-Smoke` through the native folder selector. The initially launched package was stale: its Entity build still reported `entity.shadow_mismatch` after a valid portable-record edit, proving that it predated the authoritative compiler cutover.

The stale package also reproduced an unsafe editor sequence. `GUI_SMOKE_ENTITY/meta.yaml` accepted `title: [unterminated` and wrote it to disk. Discard then exposed an incoherent old editor baseline. This was not merely a visual problem: the malformed YAML was confirmed in the selected disposable project. The repaired Apply boundary now rejects that source before writing, and the frontend preserves the dirty draft for correction.

The disposable smoke project was synchronized file-for-file with PIHC3 `8cc1bf65f` for `system/entity_family.py`, `system/entity_compiler.py`, `system/entity_records.py`, and the aggregate metadata. Its distinct project id, title, project-local output path, and intentional GUI edit fixtures were preserved. The protected PIHC3 checkout at `/Users/magolor/Projects/ParaDev/ParaDev-3/projects/PIHC3` was not mutated.

## Authoritative edit verification

The two edits made through the packaged GUI before the safety patch remain valid authoritative inputs:

- `entity/VIENTO_MIRROR/record.json`: mesh scale `4.0 -> 4.25`;
- `entity/VIENTO_AIR_AIRSHIP/record.json`: first entity scale `1.0 -> 1.125`.

With the synchronized compiler, a real Entity-family plan and emitted build completed with 136 modules, 189 total artifact rows including two project descriptors, zero diagnostics, and zero errors. The aggregate owns exactly 182 artifacts: nine generated PDX files and 173 copied static assets. The novice `GUI_SMOKE_ENTITY` owns five artifacts.

The emitted `gfx/models/00_hoi4dev_meshes.gfx` contains `VIENTO_MIRROR_mesh` with `scale = 4.25`. The emitted `gfx/models/z_hoi4dev_entities.asset` contains `VIENTO_AIR_AIRSHIP_entity` with `scale = 1.125`. The source map attributes the generated outputs to the edited `record.json` files, attributes `legacy/entities.json` only to the generated unit-entity output, and does not use a golden PDX file as compiler input.

An invalid semantic Apply setting `VIENTO_MIRROR.mesh.scale` to `0` was exercised both through local source and through the final packaged one-file backend protocol. Both returned the precise portable-record error and preserved the record SHA-256 `a80a5fa9053fbbe124c31b6ca044c49c02f9b23dcb6fc46f695b1e8292f49de9`.

## Package verification

The first package command successfully built and ad-hoc signed `ParaDev.app`, but styled DMG creation failed after a silent 120-second Finder step. macOS unified logs identify a TCC Automation denial: `osascript` was not permitted to send AppleEvents to Finder (`-1743`). The app and temporary read-write image were valid; this was not a compiler, application, or signature failure.

The final package used the supported non-Finder path:

```bash
rtk bash scripts/build-tauri.bash --headless-dmg --adhoc-sign
```

It completed successfully, verified the DMG CRC, mounted the image read-only, verified the mounted app and bundled backend signatures, and verified `Applications -> /Applications`.

- DMG: `80,439,284` bytes, SHA-256 `1fdaea204f1a83f5855ffe0d4b619b58fa5f3ca35e1f038cdff359744a48e89b`;
- desktop executable: SHA-256 `49c5dee16cea9b23f711ab2b8ae84efb891e017fa3781d7fae5eb799a78e5a29`;
- bundled backend: SHA-256 `b9ff20990f60b431a35b901cbbf138c028cb62074b2fb3c74203e0f78f5f6901`.

The packaged runtime reports ParaDev `0.1.0.000dev`, HeavenBase `0.1.2.0`, Python `3.12.13`, Darwin arm64. Developer ID signing, notarization, stapling, and clean-machine Gatekeeper testing remain distribution requirements; ad-hoc signing is for local QA only. A styled DMG remains a separate manual test in a process granted Finder Automation permission.

## Verification

- ParaDev full fast gate: 1,478 passed, one expected PIHC fixture-sync skip, one warning.
- ParaDev `tests/test_project.py`: 251 passed.
- Structured draft subset: 29 passed, including whole-request no-write and recursion normalization.
- REST/project API focused gate: three passed.
- Desktop frontend full unit gate: 967 passed across 56 files.
- Focused desktop editor tests: 64 passed.
- TypeScript/Vite production build: passed; only the existing large-chunk warning remains.
- PIHC3 Entity-family route suite: 35 passed, including seven source-text validator cases.
- Black, Flake8, and `git diff --check`: passed.
- Heaven-style scan: PIHC3 changed Python paths clean. ParaDev's broad `project.py` scan continues to report its existing `os`, `shutil`, and `pathlib` imports plus the narrow PyYAML exception import; YAML parsing itself routes through HeavenBase `loads_yaml`.
- Final headless DMG integrity, mounted signature, and Applications-link checks: passed.

## Remaining release boundaries

The final post-fix visual Apply/Discard loop is still pending because macOS auto-locked during the long native builds and Computer Use cannot unlock it. Once unlocked, the next packaged pass is: reject malformed YAML without disk change, reject `mesh.scale = 0` without disk change, retain both dirty drafts and accessible errors, repair each draft, rebuild the Entity family, leave and return to the Build rail, and confirm current progress/interrupt state.

Other known product work remains: novice-facing structured Entity record and assignment forms, optimistic source revisions to prevent external overwrite, transactional rollback across unexpected multi-file commit failures and source-plus-rename operations, durable active-build recovery across rail unmount/app restart, structured blocked-build diagnostics from child stdout, serialization of overlapping partial builds, safe Entity rename/removal policy, and PDX buffer validation before Apply.
