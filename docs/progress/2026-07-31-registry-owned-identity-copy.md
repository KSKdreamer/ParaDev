# Registry-owned module identity copy

Date: 2026-07-31

## Outcome

- Module duplication now creates an independent logical module by default.
  The selected build family rewrites owned paths and exact identifier tokens
  in UTF-8 sources while preserving binary assets.
- Exact path-and-byte copying remains available only through the explicit
  `identity="preserve"` compatibility mode.
- Plans include the target paths, target hashes, rewrite counts, and rewriter
  identity. Apply still requires the exact current plan hash and uses the
  existing crash-safe staging, publication, verification, and rollback
  transaction.
- The desktop review explains the independent-copy behavior and reports
  rewritten files and renamed paths instead of telling users to repair a
  literal copy manually.

## HeavenBase extension boundary

- Standard source-family dataclasses own `identity_rewriter`; Registry views
  expose the capability as `authoring.identity_copy`.
- `BuildRegistry.identity_rewriter_for(...)` is the only SDK resolution seam.
  The SDK, CLI, REST, MCP, and desktop contain no family-name dispatch.
- A project-local external Entity family test proves that a PIHC3-style
  HeavenBase extension inherits and advertises the same capability.
- HeavenBase 0.1.2.1 MCP capsule parsing is covered by the live toolkit test;
  its bounded docstring parser receives an unwrapped identity parameter row.

## PIHC3 source audit

- The live `projects/PIHC3/src/modules` tree contains zero directories ending
  in `_component` or `_asset_component`, and zero `legacy`,
  `inactive_modules`, or empty directories.
- It contains 14,618 physical module folders across 75 registered source
  families. The checked-in migration contract validates every direct module
  and collection folder as `id - preferred-language title`.

## Verification

- Python: 2,196 passed; nine native-Windows tests skipped.
- Desktop: 87 files and 1,415 tests passed.
- TypeScript/Vite production build passed.
- PIHC3 clean and cached: 14,617 active modules, 106 collections, 35,139
  artifacts, zero diagnostics.
- Technology family partial: 300 modules, 11,899 artifacts, zero diagnostics.
- `technology/TECHNOLOGY_FIREARM_I` partial: one module, 10,997 artifacts,
  zero diagnostics.
- Changed-file Black/Flake8 gate and repository-wide Flake8 passed.
  Repository-wide Black still reports pre-existing formatting drift in 24
  unrelated dirty files; those files were not rewritten as part of this
  transaction.
- Generated TypeScript and Markdown API references match the SDK renderers;
  repository diff check passed.

## Next

- Continue reducing non-programmer authoring burden through Registry-owned
  family templates and source-slot forms.
- Add family-specific identity rewriters only when a concrete PIHC3 grammar
  needs behavior stricter than the safe default token rewriter.
