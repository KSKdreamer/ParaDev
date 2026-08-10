# PIHC3 Source Cutover And Collection Localization

Date: 2026-08-03

## Outcome

PIHC3's physical authoring tree is fully cut over to semantic module and
collection families. Under `projects/PIHC3/src/modules` there are zero
`*_component`, `*_asset_component`, `legacy`, `inactive_modules`, symlinked,
or empty directories. The live inventory is 70 module families, 14,574
authored modules, two collection families, 90 authored collections, and
36,469 authored source files. Every direct source unit uses the canonical
`id - preferred-language title` form.

The old component folders still visible in source-control or history views
belong to the nested PIHC3 repository's pre-cutover `HEAD`. They are deleted
from the physical working tree; the canonical replacements are currently
untracked until the large migration is reviewed and committed as one unit.
They are not compiler inputs and must not be restored.

`scripts/check_source_layout.py` is the build preflight and reproducible source
of truth. It rejects retired directories and object ids, empty or copied
source paths, symlinks, loose family files, duplicate identities, malformed
folder titles, empty source units, and visible system-owned metadata before
discovery can cache a bad layout. The focused 151-test PIHC3 migration gate
also exercises synthetic forbidden trees and the exact live inventory.

Collection-owned localization now uses the same Registry-owned authoring
contract as module localization. `Project.localization_workspace(...)` and
`Project.plan_localization_update(...)` accept a discriminated module or
collection target and return v2 payloads with one nested target identity and
`unit_relative_path` source ownership. REST exposes neutral
`localization.workspace` / `localization.plan` operations, MCP exposes
`localization_workspace` / `localization_plan`, and the desktop collection
inspector renders the same guarded cross-language table used by modules.
Decision-category SDK, REST, MCP, and desktop tests prove that planning remains
read-only until source edits are explicitly applied.

## Verification

- PIHC3 source layout and migration contracts: 151 passed.
- Localization, surface, desktop-backend, MCP, and architecture focus gate:
  241 passed.
- Python fast gate: 2,392 passed, nine native-Windows skips, one warning.
- Desktop: 92 files and 1,479 tests passed.
- Rust/Tauri: 96 tests passed across three suites.
- TypeScript and Vite production build passed; the existing large-chunk
  advisory remains.
- Black/Flake passed, and the changed-file diff has no whitespace errors.
- Clean/full and cached/full PIHC3 builds: 14,573 active modules, 106 build
  collections, 33,437 artifacts, zero diagnostics/errors.
- Focus-family partial: 738 modules, 28 collections, 10,802 artifacts, zero
  diagnostics/errors.
- Focus-module partial (`FOCUS_C12_SHADOWS_OF_THE_PAST`): 129 modules, one
  collection, 9,556 artifacts, zero diagnostics/errors.

## Remaining boundary

The working tree is intentionally not staged or committed from this shared
session. Until the nested PIHC3 cutover is committed, Git history continues to
show the retired component paths even though disk, preflight, and all four
build modes use only the canonical tree. The next product slice can continue
from the generic localization target contract and high-traffic collection/tree
authoring UX without restoring compatibility aliases.
