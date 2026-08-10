# PIHC3 Building Icons Implementation Plan

Date: 2026-06-29

## Steps

1. Extend the PIHC3 building family with an `icon` copy source slot.
2. Add tests covering:
   - building family icon slot registration;
   - system/vanilla building import into source modules;
   - per-building icon extraction and sentinel-frame handling;
   - generated strip frame count and emitted `icon_frame` remapping.
3. Update `migrate_pihc2_buildings.py` to merge current HoI4 and PIHC2 building sources, write per-module icons, and record icon metadata.
4. Exclude the legacy `building_icon_strip.dds` from the remaining interface-component import so the generated atlas is not treated as source.
5. Add a HoI4 building icon strip post-processor and call it after output artifacts are written.
6. Regenerate PIHC3 building/interface sources and verify the emitted mod output.

## Verification

- Focused PIHC3 building migration tests.
- Focused HoI4 building icon post-processor tests.
- PIHC3 build output check for generated strip dimensions, generated `noOfFrames`, and remapped `icon_frame` values.
- Heaven-style scan on changed Python paths.
