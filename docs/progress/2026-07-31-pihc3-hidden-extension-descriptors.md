# PIHC3 hidden extension descriptors

Date: 2026-07-31

## Outcome

- Moved all 76 PIHC3 HeavenBase Registry descriptors from visible
  `extensions/<family>/meta.yaml` files to system-owned
  `extensions/<family>/.paradev/meta.yaml`.
- Kept each extension's editable Entity, compiler, diagram provider, and hook
  code visible in its co-located `__init__.py`.
- Added ParaDev discovery for either a standard root descriptor or the hidden
  project convention. Having both is an error.
- Hidden project descriptors are staged as exact standard HeavenBase module
  folders and still enter the same HeavenBase 0.1.2.1 install, inspect,
  resolve, and activation path.

## Safety

- Staging compares normalized whole-extension content digests before and after
  copying and compares the staged artifact to the same digest.
- Symbolic links are rejected.
- `.paradev/` system files other than the descriptor are not captured in the
  executable HeavenBase artifact.
- `scripts/hide_project_extension_metadata.py` is dry-run by default. Apply
  creates a same-filesystem hard link before removing the visible name, so a
  crash cannot remove the descriptor's last name. A rerun removes a verified
  byte-identical duplicate.
- The migration is idempotent; the PIHC3 post-migration plan contains zero
  remaining moves.
- PIHC3's `.gitignore` explicitly versions only
  `extensions/**/.paradev/meta.yaml`; extension caches and ordinary
  project-local `.paradev/` state remain ignored. A clean-checkout contract
  test rejects regressions that would hide descriptors from Git.

## User mental model

```text
extensions/<family>/
  __init__.py             # editable extension implementation
  .paradev/
    meta.yaml             # generated Registry contract
```

Ordinary PIHC3 module authors work only in `src/modules/` and use the GUI or
SDK creation flows. Extension developers edit the Python implementation;
generated Registry metadata no longer competes for attention at the folder
root.

## Regression gates

- Python: 2,182 passed; nine native-Windows filesystem tests skipped.
- Desktop: all 87 files and 1,415 tests passed.
- Rust/Tauri: all 93 tests passed.
- TypeScript/Vite production build passed.
- Hidden/visible discovery, staging, ambiguity, migration idempotence, and
  conflicting-duplicate tests pass.
- All PIHC3 extension-layout contract tests pass, and the localisation
  postprocessor resolves from its hidden descriptor through the same Registry
  path.
- Full/cached PIHC3 plan: 14,617 modules, 106 collections, 35,139 artifacts,
  zero diagnostics.
- MIO family partial: 7 modules, 11,001 artifacts, zero diagnostics.
- MIO module partial: 1 module, 10,995 artifacts, zero diagnostics.
- Changed-source lint and both main/nested repository diff checks passed.
