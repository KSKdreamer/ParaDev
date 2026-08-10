# PIHC3 Building Icons Design

Date: 2026-06-29

## Goal

PIHC3 building modules should own their icon assets directly. The HoI4 `GFX_buildings_strip` atlas is a generated compatibility artifact, not the source of truth. This lets PIHC3 carry current HoI4 system buildings, PIHC-only buildings, and future high-resolution redesigns without relying on stale frame numbers copied from a compiled strip.

## Source Model

- Every normal `building` module may contain one `icon.png`, `icon.dds`, or `icon.tga`.
- The module code / object id is the stable identifier. The icon file follows the module.
- Imported current HoI4 buildings become PIHC3 `building` modules so vanilla/system icons can be redesigned alongside PIHC buildings.
- `spawn_points` and non-frame support entries remain building-family support modules and do not require icons.
- Legacy `icon_frame` values remain as provenance in source metadata and source PDX, but emitted mod output may remap them.

## Import Policy

- Current HoI4 building definitions provide the base system-building set.
- Compiled PIHC2 building definitions override matching HoI4 building definitions, preserving PIHC gameplay changes.
- Icons for building ids present in current HoI4 are cropped from the current HoI4 strip.
- Icons for PIHC-only building ids are cropped from the PIHC compiled strip.
- Invalid, sentinel, or out-of-range frames are not cropped; the module records that no source icon was extracted.

## Build Policy

- The build post-processor reads building modules and their `icon.*` sources.
- It assigns one generated atlas frame per icon-backed building module in deterministic building id order.
- It writes `gfx/interface/buildings/building_icon_strip.dds` into the emitted mod output.
- It rewrites emitted `common/buildings/{id}.txt` `icon_frame` fields to the generated frame numbers.
- It updates emitted `interface/countrystateview.gfx` `GFX_buildings_strip.noOfFrames` to match the generated atlas.

## Non-Goals

- Building effects and gameplay logic stay in `def.txt`; the icon work only changes source assets and emitted UI compatibility files.
- The source `interface/countrystateview.gfx` can keep a legacy frame count because the emitted output is generated.
- The first implementation uses ImageMagick for DDS crop/append because the project already treats Wand/ImageMagick as the HoI4 image pipeline.
