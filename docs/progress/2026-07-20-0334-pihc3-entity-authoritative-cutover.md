# PIHC3 authoritative Entity compiler cutover

Date: 2026-07-20 03:34 +08

## Outcome

PIHC3's 134 portable Entity records and editable assignment table are now the authoritative source for all nine generated Entity PDX files. Full Entity-family and full-project builds emit those nine generated files plus the existing 173 static assets under the single owner `module:entity/HOI4DEV_ENTITIES`. Valid record and assignment edits change usable mod output; invalid or incomplete corpora fail closed without planning any aggregate artifact.

The cutover is pushed to PIHC3 draft PR #2 at `803b6b615` (`feat(entities): make record compiler authoritative`). ParaDev's supporting loader, capability-contract, and acceptance changes are pushed to draft PR #4 at `2296237` (`feat(build): isolate project plugin dependencies`) and `3a956d51` (`test(pihc3): verify authoritative entity output`). The earlier project-module dataclass registration fix remains at `bbeb9bce`.

## Authoritative build contract

`EntityFamily` now uses a dedicated `compiled_records` route. The aggregate route delegates only static copies; the project-local compiler creates all nine PDX artifacts from the complete record and assignment corpus. The checked-in PDX files remain non-emitting golden evidence used by independent parity tests and importer verification, never artifact inputs or fallback output.

The build contract is nine-or-zero:

- exactly one `entity/HOI4DEV_ENTITIES` aggregate and all 134 ordered `legacy_record` modules are required;
- the compiler emits nine unique PDX paths and the aggregate copies 173 contracted static paths;
- the 173-path inventory is pinned separately from file bytes, allowing in-place binary replacement while blocking missing, substituted, or extra paths;
- aggregate-only and partial-corpus builds report `entity.compiler_incomplete_records` and emit no aggregate artifacts;
- complete records without the aggregate report `entity.compiler_missing_aggregate`;
- invalid compiler inputs report a source-linked error and emit no aggregate artifacts;
- unrelated novice-authored `basic` Entity artifacts remain visible in a blocked plan.

Generated artifact provenance now contains real authoring inputs. Every PDX artifact lists its contributing `record.json` files; the unit output additionally lists `legacy/entities.json`; mesh output lists relevant aggregate static sources; owner-local animation outputs list their `.anim` sources. No generated artifact cites a golden PDX snapshot.

## Review fixes

The post-cutover architecture review found three P1 and two P2 defects, all repaired before commit:

- invalid aggregate metadata previously blocked the build but still left aggregate artifacts in the plan;
- deleting an optional static file could silently reduce the aggregate to 172 copies;
- direct `system.*` imports could reuse another project's cached compiler, and one standalone acceptance fixture omitted required sibling files;
- mixed edits could heuristically attach a semantic compiler failure to the wrong record;
- registry inspection advertised only copied output for `compiled_records`, hiding its generated PDX capability from API and GUI consumers.

Emission now independently revalidates compiler-owned modules and fails closed. Static paths are checked against the fixed 173-path contract. Compiler errors carry structured record, assignment, or static provenance rather than hash-edit guesses. ParaDev loads project plugins in project-hashed synthetic namespaces, supports safe relative sibling imports, reloads changed dependencies, quarantines legacy absolute imports during registration, and serializes import-state mutation. Families can declare validated `generated_outputs`, and PIHC3 advertises compiler-owned PDX output for the `compiled_records` route.

## Verification

- PIHC3 full script suite: 249 passed in 25.58 seconds.
- Entity family routing, edit, attribution, and fail-closed suite: 28 passed.
- Pure compiler suite: 4 passed.
- ParaDev registry/project-build gates for plugin isolation and generated outputs: 91 passed.
- ParaDev project suite: 245 passed.
- ParaDev Python-plugin focused gates: 26 passed.
- ParaDev PIHC3 Entity acceptance: 4 passed, including family inspection, complete build semantics/source maps, standalone novice template flow, and importer regeneration.
- Black, Flake8, Heaven-style scan, and `git diff --check`: passed; the scan reports only pre-existing broad-file import notices.
- Final isolated Entity plan and emitted build: 135 Entity modules, 184 total artifacts including two project descriptors, zero diagnostics/errors, nine generated PDX files, 173 byte-identical static copies, all nine PDX files parse, all 134 records appear in provenance, assignment provenance appears only on the unit output, and no golden PDX is an input.
- Final isolated clean full PIHC3 build: 18,175 modules, 78 collections, 37,556 artifacts, zero diagnostics/errors, `blocked: false`, and exit status 0. Localization postprocessing also exited 0 after finding 6,073 duplicate keys, removing 6,088 entries, changing 1,672 files, and moving 3,338 files. The verification snapshot hash-matched PIHC3 `803b6b6158483b4d17cc96713ec944cf06b5b1b0` and ParaDev `3a956d516d863d4015c2fda4d66144c8e3b0407f`.

## Packaged GUI state and sequencing note

The user selected the disposable PIHC3 GUI project successfully. The packaged app retained that selection, but macOS Computer Use continued to report the desktop locked even after selection, so UI automation could not safely inspect or manipulate the app.

The prior report recommended completing the old shadow-mismatch repair loop before ownership cutover. Because the locked desktop made that loop unavailable while deterministic backend acceptance remained fully testable, this slice proceeded backend-first under stronger cutover tests. The required packaged acceptance is now: make a valid record edit and confirm generated output changes while the build stays green; make an invalid semantic edit and confirm its precise source-linked error; repair it through the GUI and return to green. No shell, browser, or AppleScript workaround was used for GUI testing.

## Next boundary

Repeat the valid-edit, invalid-edit, and repair-to-green workflow in the packaged Tauri app as soon as Computer Use can access the unlocked desktop. After that, continue novice-facing structured Entity forms and guided assignment editing. Public distribution still separately requires Developer ID signing, notarization, stapling, and clean-machine Gatekeeper testing.
