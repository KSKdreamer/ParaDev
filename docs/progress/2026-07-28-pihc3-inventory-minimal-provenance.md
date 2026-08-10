# PIHC3 inventory minimal-provenance checkpoint

Date: 2026-07-28

## Outcome

All 80 PIHC3 `inventory_item` modules now expose only title metadata and their
real authoring sources. The former visible `legacy/` trees moved to hidden
`.paradev/evidence/` without changing any evidence byte, and each module now
has a deterministic portable `.paradev/import.yaml`.

The production importer and its pinned safety fixture produce the same compact
layout. Importer ownership moved from novice-facing tags to the hidden import
contract while the shared transaction helper keeps tag and legacy-provenance
recognition for existing importers.

## Verification

- Evidence parity: 301 files and 9,918,643 bytes; aggregate SHA-256 remained
  `f3d1ef6504b803a494f377554d9f4e666ebfd20d25d96e56dd579a1d27c11a82`.
- Inventory importer safety: 21 passed.
- Standard pinned importer-safety gate: 2 passed, 1 expected live-sync skip.
- Focused PIHC3 inventory contracts: 2 passed, 308 deselected.
- Emitted inventory family parity: 80 modules, 11,315 artifacts, zero
  diagnostics, and 11,314 output files totaling 65,928,459 bytes.
- Pre/post output digest:
  `e42b9bea330df1ab90e9217bd5bd48076b0cf5d6e3b34b173a3dde10b995e15c`.

## Remaining boundary

Inventory scan/debug aggregation, scripted GUI/interface assembly, operation
buttons, and scripted-localisation selectors remain separate functional
authoring slices. This checkpoint changes source organization and provenance,
not compiled gameplay output.
