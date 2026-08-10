# PIHC3 Built-in Family Overlays

Status: complete

Date: 2026-08-10

## Outcome

PIHC3 Idea and Event now follow the minimal HeavenBase extension boundary.
They are standard HoI4 families, so the built-in module/family model owns
persistence. PIHC3 contributes only behavior that is actually project
specific.

The title-only `PIHC3Idea` and `PIHC3Event` Entity classes and their empty
HeavenBase extension definitions were removed. Each hidden descriptor now
contains one `paradev_build_family` target and its authoring template. The
Python module exposes a thin compiler overlay with the existing resource
slots, Registry field hints, routing, diagnostics, emit behavior, and
`replaces_registered_family` hook.

Idea still owns exact compiled Idea resources and source-path-preserving shared
PDX. Event still owns event-picture resources and collection/module event
routing. No GUI family switch or alternate compiler was introduced.

## HeavenBase proof

- A fresh module Registry resolves `pihc3-idea` and `pihc3-event` as build
  families and reports both old Entity identifiers as unknown.
- A cold isolated Catalog refresh completed successfully with 765,033 rows,
  zero diagnostics, only the built-in `hoi4` extension, and its 16 canonical
  Entity types.
- The temporary cold Catalog exceeded 1 GB because PIHC3 currently indexes
  454,836 PDX symbols among its complete source/build graph. It was deleted
  after verification and did not modify the project Catalog.

## Compilation proof

- Cached full: 14,573 modules, 106 collections, 33,437 artifacts, zero
  diagnostics.
- Idea family: 392 modules, 10,490 artifacts, zero diagnostics.
- Event family: 42 modules, 11,072 artifacts, zero diagnostics.
- `idea/IDEA_C01_ANGRY_ANGRY_1`: one module, 9,300 artifacts, zero
  diagnostics.
- `event/C01_MAIN`: one module, 9,362 artifacts, zero diagnostics.
- The 33,436 compiler-owned output artifacts retained exact digest
  `ba17e0ffda128cc5b142f244d36de0ced7775335635fdd530ab4bee47ef83038`.
  The one build-root artifact retained digest
  `c6bbe093a0341bd460860a957331887ee95e9b1f0cdfe3278279a14a550e12b4`.

## Verification

- PIHC3 extensible-layout integration suite: 33 tests passed.
- Repository-wide Python gate: 2,570 tests passed with 9 expected native-Windows
  filesystem tests skipped on macOS.
- Targeted repository-profile Black, Flake8, and whitespace checks passed.
