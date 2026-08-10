# PIHC3 authoring completeness and portable artifacts

## Outcome

This checkpoint closes several gaps found by exercising the complete PIHC3 catalog against the latest local HeavenBase source. ParaDev now exposes metadata and component-family sources for direct editing, keeps HeavenBase Catalog projections synchronized after source writes, rejects scaffolds that cannot become valid family modules, preserves every duplicate source-file identity in the editor, and blocks output paths that would collide on case-insensitive filesystems.

The PIHC3 acceptance clone now plans successfully with 18,040 modules, 78 collections, 37,558 artifacts, zero diagnostics, and zero independent Unicode-NFC/casefold collision groups. The original local PIHC3 worktree was not modified; its pre-existing dirty state was preserved exactly.

## Authoring changes

- The metadata filenames actually consumed by the loaders are exposed as synthetic, no-follow `meta` sources: `meta.yaml` for modules and `meta.yaml` or fallback `collection.yaml` for collections. This includes HeavenBase Catalog-backed module rows, so the editor's Name field can produce a real metadata source edit instead of a UI-only draft.
- A source draft contained by one canonical module now materializes that module again under the Catalog writer lock and returns the same additive `catalog_mutation` contract used by create, rename, and remove. The desktop reconciles the delta or latches its existing dirty-Catalog recovery state.
- Template scaffolds are matched against the destination family's required slots before any files are written. The previously false-green entity-shaped template pattern is now blocked when its rendered paths cannot satisfy the registered family.
- Templates explicitly marked `authoring_ready: false` are unavailable in the novice creation flow. If a family has no usable template, New is disabled with an English/Chinese explanation instead of opening a dialog that cannot succeed.
- Template fields now use their SDK-declared controls and validation: multiline text, choices, booleans, numbers, asset identifiers, required values, defaults, descriptions, and advanced fields.
- Component families are no longer hidden from the Modules workspace. This exposes the 42 PIHC3 component families that were previously absent from the editor.
- Every source file receives a stable draft identity. Duplicate slots and same-name template paths can be selected and saved independently; script-like `.gfx`, `.asset`, `.gui`, `.mesh`, `.anim`, `.fnt`, `.lua`, `.csv`, and `.xml` files open as code rather than images.
- Modules with several raster sources now provide an image-source selector and target replacement at the selected source instead of silently operating on the first image.
- Existing PNG sources must overwrite their exact selected source path. Non-PNG sources are blocked at both UI and model boundaries with localized conversion-required guidance, so DDS/TGA/JPEG/WebP/BMP editing can no longer create an ignored sibling PNG or report a false successful apply.

## Build and portability changes

- Artifact collision validation now normalizes every target path with Unicode NFC and case folding. Distinct spellings are blocking even when their bytes are identical, preventing a build that works on a case-sensitive temporary volume but overwrites files on common Windows and macOS installations.
- The HoI4 building-icon postprocessor returns artifact deltas for the generated strip and every rewritten building/interface file. The final `BuildResult`, artifact manifest, and source map receive the postprocessed hashes, sizes, owners, inputs, and copy-source provenance before manifests are written.
- Rewritten generated sprite payloads now carry the final `noOfFrames` value used by `sprites.json`, and a late generated building strip preserves the standard `copy_root.shadowed_artifact` warning if it replaces a copied strip.
- In an isolated copy-on-write PIHC3 clone, all 35 known case-only collision pairs were repaired:
  - the 33 redundant lowercase `idea_category` icon copies were removed from the family output contract while their source icons and identical uppercase `idea_asset_component` outputs were preserved;
  - the two C08 joint-command civilian portrait files were moved to explicit `_default` names and current module/GFX references were updated;
  - legacy source paths remain recorded, with explicit portable-path rename provenance.

The artifact count moved from 37,591 to 37,558 exactly as expected: minus 33 redundant idea-category copies, with the two portrait removals and two additions count-neutral. Sixteen unrelated balance-of-power copy artifacts remain present.

The portable repair was then reproduced from clean PIHC3 `v3.1` HEAD in a separate linked worktree. That branch built 18,038 modules, 78 collections, and 37,552 artifacts with zero diagnostics/collisions, excluding every unrelated change from the user's dirty PIHC3 worktree. [HOI4-PIHC PR #1](https://github.com/Magolor/HOI4-PIHC/pull/1) was squash-merged into `v3.1` as `6cb2ab690954815f834e04b0cd5e12cf7793510c`.

## Verification

| Gate | Result |
| --- | --- |
| Complete Python suite | 1,433 passed |
| Complete desktop Vitest suite | 923 passed across 55 files |
| Desktop production build | passed; existing large-chunk advisory remains |
| Complete Tauri Rust gate | 42 passed across 3 suites |
| Desktop/native-web/Tauri Python bridge suites | 97 passed |
| Repository lint | passed |
| Whitespace/diff validation | passed |
| Latest-source repaired PIHC3 dry build | 18,040 modules; 78 collections; 37,558 artifacts; 0 diagnostics; not blocked |
| Latest-source repaired PIHC3 full emit | 18,040 modules; 78 collections; 37,559 artifacts; 0 diagnostics; not blocked |
| Independent portable-path audit | 0 Unicode-NFC/casefold collision groups |

The emitted result contains one additional postprocessed artifact: `gfx/interface/buildings/building_icon_strip.dds`. It appears exactly once in the returned result, `artifacts.json`, and `source-map.json`; all 73 postprocessed files (71 building definitions, `countrystateview.gfx`, and the strip) match their returned and persisted SHA-256/size metadata. The strip has 71 module sources, is 156,992 bytes, and has SHA-256 `8f3594ff6ec17b3f7865ebdfb05ddd66258cdfe500363837fc0e80bf5e9f4941`.

The Heaven-style scanner continues to report the repository's existing `pathlib`, `os`, `shutil`, `subprocess`, and JSON utility migrations in touched legacy modules. This checkpoint adds no new banned standard-library import category; the broader utility migration remains tracked work.

## Remaining risks and next work

- DDS/TGA/JPEG/WebP/BMP sources are now honestly read-only instead of false-green. Full image editability still requires a format-aware, dependency-checked conversion operation that atomically replaces the selected source; writing PNG bytes under another extension is not acceptable.
- The merged collision repair intentionally excludes unrelated uncommitted changes in the user's original PIHC3 worktree. That worktree remains untouched and will need a deliberate reconcile with updated remote `v3.1` after its local changes are secured.
- PIHC3 still contains an obsolete machine-local absolute copy root, source/output parity tools tied to older output paths, ten known idea-localization value differences, and 417 explicitly identified trait-formatting differences.
- Collection create/rename/remove, domain-backed diagram mutations, template coverage for the remaining families, and decomposition of the aggregate entity source remain incomplete.
- Native Tauri visual acceptance and final packaging remain blocked by the locked macOS GUI session. Prior native-web acceptance remains green, but it is not a substitute for the final native/package pass.
