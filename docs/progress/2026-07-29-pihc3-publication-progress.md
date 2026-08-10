# PIHC3 publication-validation progress

Date: 2026-07-29

## Outcome

ParaDev now emits an SDK-owned `validating_publication` progress event after
artifact planning and before publication ownership/path preflight. Large PIHC3
builds no longer appear idle while checking tens of thousands of existing
generated destinations.

The event is shared by CLI, desktop, and direct SDK builds. The desktop maps
the phase to **Validating publication** / **验证发布安全性** while retaining the
backend artifact count and detail. No GUI-side compiler timer, cache estimate,
or parallel publication implementation was added.

## Verification

- Python progress contracts: 2 passed.
- Desktop focused build-page/model contracts: 67 passed.
- Desktop complete gate after a locked dependency restore: 85 files and 1,405
  tests passed.
- Desktop production TypeScript/Vite build passed.
- Real isolated PIHC3 publication:
  - clean/full: 14,617 modules, 106 collections, 35,139 artifacts;
  - cached/full: 14,617 modules, 106 collections, 35,139 artifacts;
  - Focus family partial: 738 modules, 28 collections, 12,499 artifacts;
  - `technology/TECHNOLOGY_FIREARM_I` module partial: 1 module, 10,997
    safely scoped artifacts.
- Each mode emitted exactly one `validating_publication` event at 75%, returned
  zero diagnostics/errors, and remained unblocked.
- Both partial builds preserved all 35,139 published files and a complete
  35,139-row ownership ledger with `whole_project_baseline: true`.

## Next

Continue the PIHC3-first usability loop with the highest-friction guided
authoring or diagram workflow. Keep domain behavior in the SDK/project
extensions and use the desktop only as a typed presentation adapter.
