# PIHC3 Launcher Registration Stability

## Outcome

The active `PIHC (Dev)` playset now contains one enabled, `ready_to_play` local PIHC3 entry. A real clean PIHC3 compile completed while Paradox Launcher remained open without changing the output-directory identity, launcher-descriptor identity, or playset mod identity. The launcher warning did not return.

## Root Cause

The PIHC3 clean wrapper deleted both the live HOI4 mod directory and its outer `.mod` file before rebuilding. Launcher logs recorded an `ENOENT` size scan during that interval. The launcher retired the original local-mod record, registered the restored path under a new internal id, and left the active playset attached to the unavailable record.

The descriptor path and syntax were valid. The immediate fault was the stale playset association, not an unrecognizable PIHC3 folder.

## Repair

- Rebound `PIHC (Dev)` through the launcher UI to the current PIHC3 `0.2.3` entry and removed the unavailable `0.2.3.007dev` entry.
- Changed ParaDev full rebuilds to clear registered HOI4 output contents while preserving the output directory itself.
- Made launcher synchronization skip semantically unchanged PDX descriptors, including the field order and missing final newline produced by the launcher itself.
- Kept malformed launcher descriptors recoverable by replacing them from the generated source.
- Changed the PIHC3 clean wrapper to preserve `PIHC3/` and `PIHC3.mod`, removed its redundant descriptor copy, and routed cleanup, emission, and launcher sync through one absolute mod root.
- Removed PIHC3's hard-coded manifest output root so environment overrides cannot split cleanup from compilation.

## Verification

- Live clean compile: 18,175 modules, 78 collections, 37,556 artifacts, zero diagnostics, zero errors, `blocked: false`.
- Post-build launcher database: one enabled PIHC3 playset member, status `ready_to_play`, version `0.2.3`; integrity check `ok`.
- Output directory and outer launcher descriptor retained their pre-build filesystem identities; the semantically unchanged outer descriptor also retained its timestamp.
- Launcher UI home screen remained free of the missing-on-disk warning after the clean compile.
- ParaDev project-build and CLI regression suites: 252 passed.
- PIHC3 project-local suites: 259 passed.
- Broader PIHC3 migration-contract inventory: 278 passed and 43 failed. All 43
  remaining failures reproduce against the pre-change ParaDev and PIHC3 commits
  and cover importer/parity work across entity families; none is in the
  launcher-registration, build-cleanup, descriptor-sync, wrapper, or output-root
  contracts changed here.

## Residual Risk

A clean/full build intentionally clears the contents of the live output directory before repopulating it. ParaDev disables its own Run Game action for an active build, but starting HOI4 directly from another launcher during that interval can still observe a partial mod. A future staged-publish design can close that concurrency gap without weakening launcher identity stability.
