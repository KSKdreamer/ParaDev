# Registry diagram renderer adapters

Date: 2026-08-01

## Outcome

- Replaced four family-shaped projection/diff/apply branches in the desktop
  module editor with one renderer-adapter seam selected from the active
  Registry diagram capability.
- Added the shared `graph` renderer contract for external and project-local
  providers. It projects transport-neutral nodes and arbitrary relationship
  kinds, preserves localized titles, images, source paths, and reviewed
  revisions, and returns generic position and edge intents to the provider
  planner.
- Kept the specialized Focus, Technology, Doctrine, and MIO projections as
  bundled adapters. Their domain-specific source semantics remain outside the
  React editor, while MIO organization scope and node-authoring UI remain
  explicit optional capabilities.
- Hardened the external boundary: empty or whitespace-padded ids, partial or
  non-finite coordinates, unknown relative parents, dangling edges, duplicate
  nodes or relationships, and edited nodes without reviewed revisions fail
  visibly.

## Verification

- Rendered ModuleEditor lifecycle coverage loads an external Registry provider
  using `renderer="graph"`, moves a node, reviews the generic intent plan, and
  applies the exact plan hash without any external family switch.
- Generic adapter happy, edge, and error coverage passes alongside all bundled
  adapter tests. The complete desktop suite passes: 1,446 tests in 88 files.
- Strict TypeScript and production Vite build pass.
- Registry, project diagram, and live PIHC3 extensible-layout tests: 63 passed.
- Standard Python gate: 2,274 passed, with nine native-Windows tests skipped.

## Remaining scope

- The desktop intentionally does not execute arbitrary extension-supplied UI
  code. Providers use the shared graph protocol unless ParaDev itself ships a
  reusable specialized renderer.
- Family-specific create experiences continue to migrate toward provider-owned
  declarative authoring capabilities; this slice changes graph projection,
  diff, and apply routing only.
