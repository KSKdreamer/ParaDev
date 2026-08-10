# Partial-build result clarity and packaged Entity smoke

Date: 2026-07-20 17:03 +08

## Outcome

ParaDev now separates authoritative whole-project health from the latest completed partial rebuild. An older interrupted or failed full build therefore remains visible and continues to block Run Game, while a later successful Entity rebuild receives its own persistent result surface instead of disappearing into Build History.

The English and Chinese result copy states that the rebuild checked only its target and directs the user to run Build for a whole-project check. Failed and interrupted partial results provide explicit recovery guidance. This keeps the conservative launch decision intact without making a novice think that a successful family rebuild failed.

All native Entity work in this pass used the disposable project:

`/Users/magolor/Projects/ParaDev/PIHC3-GUI-Smoke`

## Status and result ownership

The prior overview deliberately preferred adverse project state. That policy was safe, but it also meant that a later successful family rebuild appeared only in history whenever an older full build had failed or been interrupted.

The model now exposes two different answers:

- `buildOverviewRuntime` remains the authoritative selector for project-wide health and launch safety.
- `latestPartialResult` selects the newest terminal targeted build for a separate result surface.

The result includes the target, terminal state, duration, completion time, and state-specific next step. Run Game also treats blocking diagnostics as a launch blocker, closing a pre-existing gap where the lifecycle could look terminally successful while the model still contained a blocking diagnostic.

## Chronology and lifecycle rules

Native `terminalSequence` values are authoritative when both candidates have them. Restored renderer checkpoints fall back to completion and start timestamps when a native sequence is unavailable.

The selection rules cover the lifecycle edges exercised during this pass:

- A newer terminal full build hides an older partial result.
- Any active full or partial build hides stale terminal partial copy.
- Optimistic starts rejected before a run exists are not presented as completed work.
- A newer rejected attempt can suppress an older result without preventing a later real sibling completion from winning.
- Partial results are isolated by exact project root even when two projects share an ID.
- Project switching cannot leak a result from the previously selected root.

## Accessibility, localization, and history clarity

The persistent result is a polite, atomic `role="status"` announcement. The surrounding status label is now “Project status” / “项目状态”, making the distinction from the partial result explicit.

Build tabs expose tab/tabpanel relationships. Build History disclosures expose expanded state and controlled content, and targeted summaries name the target. In the native Chinese regression the newest row was announced as `局部重构建 · 族 · entity`, rather than a generic rebuild with duplicated family/id text.

Success, failure, and interruption use compact green, red, and yellow treatments with 11-pixel metadata text and normal letter spacing so the result remains subordinate to project health.

## Packaged native regression

The ad-hoc-signed release bundle was launched after moving the exact stale onefile cache to a recoverable temporary backup. The package then completed a genuine cold extraction and opened normally with the remembered `PIHC3 GUI Smoke` project and all 93 discovered module families.

Observed Chinese workflow:

1. Build opened with the older interrupted full build still shown as `项目状态` and Run disabled.
2. The existing successful Entity result appeared separately with its 12-second duration and whole-project-check guidance.
3. Starting another Entity rebuild displayed the mutation confirmation.
4. After confirmation, the stale result disappeared while `局部重构建中` was active; Build and Run remained disabled.
5. The Entity row advanced from `0 / 459` to `459 / 459` source files across 136 modules.
6. The rebuild completed successfully in 12 seconds at 16:55:50 with exit code 0.
7. The overview returned to the older interrupted full-project state, preserved the Run lock, and displayed the new Entity success result.
8. Build History named the Entity target and exposed the run ID, mode, start/completion times, command, output, and error-log paths when expanded.

This is the intended conservative behavior: a targeted success is visible and useful, but it does not certify the whole project for launch.

## Same-version Nuitka cache finding

The first launch of this rebuilt `0.1.0` package returned an invalid-JSON EOF because macOS killed the extracted backend. Unified kernel logs identified `cs_invalid_page`, an mtime mismatch, and `SIGKILL` for:

`/Users/magolor/.cache/Magolor/ParaDev/0.1.0.000/paradev-backend.bin`

This is distinct from the previously fixed concurrent first-extraction race. A changed development payload reused the same cached onefile identity because the product version remained `0.1.0`; the existing extracted path was replaced while macOS still associated signature state with the old file.

The exact cache directory was preserved at:

`/private/tmp/paradev-onefile-cache-backup-20260720-1648`

After one clean extraction, the recreated 315,645,360-byte backend passed strict code-signature verification. Kernel logs from 16:54 onward contained no ParaDev `cs_invalid_page` or `cs_mtime` error, and repeated backend calls plus the Entity rebuild succeeded.

Cached onefile mode remains intentional for warm-launch performance. A dedicated packaging follow-up must give development/QA payloads a deterministic input-specific cache key and require coherent, monotonically changed Python/Tauri/Cargo/npm versions for official releases. Temporary extraction would add the roughly 20-second unpack cost to every short-lived sidecar call, while timestamp-only keys would break reproducibility and leak roughly 315 MiB per rebuild.

## Verification

- Focused current Build model/UI gate: 63 tests passed, including both mixed native-sequence/checkpoint directions.
- Full desktop frontend: 62 files and 1,132 tests passed.
- TypeScript typecheck and Vite production build: passed; only the existing large-chunk advisory remains.
- Full Python regression: 1,528 passed, one skipped, three warnings.
- Repository formatting/lint: 162 files unchanged.
- Diff whitespace gate: passed.
- Independent code and regression reviews: no remaining P0-P3 findings.
- Carried forward from the unchanged preceding backend checkpoint: 63 Rust tests, 21 Python Tauri-bridge tests, and 18 disposable Entity provider/compiler tests passed.

## Package

The package was built with `scripts/build-tauri.bash --headless-dmg --adhoc-sign`. Nuitka, Vite, Rust/Tauri release compilation, application signature verification, DMG checksum/mount, mounted-application signature, and the Applications link all passed.

The exact-head rebuild after the mixed native-sequence/checkpoint correction repeated those gates. Its packaged frontend reopened the disposable project with the adverse full-build status, latest Entity success, and disabled Run Game intact; the post-launch kernel-log window contained no new ParaDev code-signature error.

| Artifact | Result |
| --- | --- |
| Application | 79 MiB on disk; strict deep signature verification passed |
| Bundled backend | SHA-256 `5e43a215ebc0efb63dc5f0f19ba3944075480c7ab830dd7e8dc3baec5f55fe04` |
| DMG | 80,568,092 bytes |
| DMG SHA-256 | `5e1b5bc9962a96c3f21f532a957737f26033ce89bce59894478a64aa0332a4b1` |

This remains a local QA package. Public macOS distribution still requires Developer ID signing, notarization, stapling, and Gatekeeper validation on a clean machine.

## Safety invariant

The protected checkout at `/Users/magolor/Projects/ParaDev/ParaDev-3/projects/PIHC3` was never selected for mutation. A final read-only check found it clean at exact HEAD `7a4efe41bf07084ffe8fe56c2ba2f158ea14527f`; all hands-on Entity building remained in the disposable smoke project.

## Remaining boundaries

- Derive a deterministic input-specific Nuitka cache identity for changed development payloads and enforce coherent official release versions.
- Complete Developer ID and notarized clean-machine packaging.
- Continue novice-safe structural Entity authoring beyond the current scalar Guided form surface.
