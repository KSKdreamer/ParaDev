# PIHC3 Generic Diagram-node Authoring

Date: 2026-08-02

## Outcome

PIHC3 Focus creation now uses the same Registry-owned diagram edit contract as
other tree providers. ParaDev core no longer contains a PIHC3 template id, a
Focus-only project method, or separate REST, MCP, desktop-backend, Tauri, and
React creation paths. The project-local Focus extension owns its fields,
collection/tree resolution, validation, source revision, resource slots, and
module creation request.

The generic provider result can request a standalone module scaffold. ParaDev
binds that request and the provider's source-tree revision into one reviewed
plan hash, installs the whole module transactionally, validates it with the
registered family build, and refreshes the Catalog only after success. A build
rejection removes the new module again; an old plan is rejected if the tree
changes. The retained Windows adapter has the same validation-before-commit
rollback contract.

Diagram-node authoring can now explicitly opt out of requiring an existing
selection. That lets users create a root Focus from the generic provider form,
while selecting an existing Focus still pre-fills tree, parent/prerequisite,
and position values. New localization follows the project's preferred
language instead of a Focus-only English default.

## Public surface

- Creation is discovered from `module_diagram(...).node_authoring` and planned
  or applied through `module_diagram_edit` in the SDK, CLI/REST frontend
  contract, MCP, Tauri backend, and desktop.
- The removed Focus-only surface no longer appears in current code, generated
  API references, or the ParaDev authoring skill.
- The generic desktop form renders provider-owned titles and fields; it does
  not know PIHC3 template ids or Focus source layouts.

## Verification

- Complete Python gate: 2,492 passed, with nine expected native-Windows-only
  skips.
- Broad affected Python gate: 459 passed, with one expected native-Windows-only
  skip.
- Desktop: 89 files and 1,453 tests passed; strict TypeScript/Vite production
  build and Rust `cargo check` passed.
- Black and Flake8 passed on all touched Python files. The Heaven-style scan
  reported only the existing standard-library import advisories in Windows
  test modules; this slice adds no such import.
- Strict isolated PIHC3 plans remained unblocked with zero diagnostics/errors:
  - clean/full and cached/full: 14,617 modules, 106 collections, 35,131
    artifacts;
  - Focus family: 738 modules, 28 collections, 12,499 artifacts;
  - `focus/FOCUS_C01_C02_EVERFREE_FIELDTRIP`: 83 modules, one collection,
    11,161 artifacts.

## Remaining work

- Continue applying the same project-owned node-planning seam to technology,
  doctrine, and MIO creation wherever their providers still expose only
  selection defaults or template handoff.
- Continue tree-editor UX work for moving, linking, and validating nodes; this
  slice closes creation ownership and transaction safety, not every visual
  editing operation.
- Native Windows integration remains outside the current priority. Its
  retained-handle rollback behavior is unit-tested on macOS, but not claimed as
  a real-Windows smoke result.
