# PIHC3 Large-family Progressive Disclosure

Date: 2026-08-09

## Outcome

ParaDev no longer inserts every directly discovered object into the desktop DOM
when the optional project index is unavailable. Direct-discovery families now
render an initial 100-row window with an explicit, localized `Show more`
control. Search, activity filtering, range selection, filtered selection, and
whole-family selection still operate on the complete in-memory family rather
than the rendered window.

The currently active object remains rendered when it falls outside the current
window, so restoring an editor session or opening an exact object never loses
its selection merely to satisfy the row bound. Catalog-backed paging remains a
separate server-owned path and is unchanged.

## Live PIHC3 proof

The native-web desktop was exercised against PIHC3's Scripted Effects family:

- initial rendered rows fell from 8,279 to 100;
- the UI truthfully reported `Showing 100 of 8279 matching objects`;
- exact-ID search found `ADD_FOG_OF_WAR_BUILDING` across the complete family;
- clearing search restored the 100-row window;
- one `Show more` action produced exactly 200 rows and an updated truthful
  summary;
- the family inventory remained 8,279 objects throughout.

This removes a measured approximately 12.8-second, 8,279-row React/DOM render
from the no-Catalog path without hiding source content or making the optional
14-minute PIHC3 index mandatory.

## Compact family navigation

The project panel now starts with only the active module group expanded rather
than exposing all 51 PIHC3 families at once. Automatically opened groups close
when the active family moves to a different group. A group the author expands
manually remains open, so the compact default does not fight deliberate
multi-group browsing.

The state transition is resilient to asynchronous startup: PIHC3's temporary
boot placeholder can open `Other & Advanced`, but it closes when the real
active Countries family arrives. A fresh live startup showed only Countries &
Politics open and 18 family rows visible. Selecting Technologies then left
only Military & Research open, and its 301 objects used the same 100-row
progressive-disclosure contract.

## Verification

- Focused list tests: 19 passed.
- Grouped-navigation focused gate: 15 passed.
- Complete desktop gate: 93 files and 1,502 tests passed.
- TypeScript and Vite production build passed; only the existing chunk-size
  advisory remains.
- PIHC3 extensible-layout gate: 33 passed.
- Exact physical source audit: 14,574 modules, 90 collections, one visible
  metadata file, and zero layout errors.
- `git diff --check` passed for the touched files.

The compiler and source model were not changed in this UI-only slice. The
latest clean/full, cached/full, focus-family partial, and focus-module partial
PIHC3 compile matrix therefore remains the 2026-08-09 green baseline recorded
in the immediately preceding checkpoints.

## Remaining boundary

The shared worktree was not staged or committed. This checkpoint does not
declare the broader continuous release goal complete. Family-refresh state
transitions and further non-programmer authoring ergonomics remain active
priorities, without adding family-specific frontend logic.
