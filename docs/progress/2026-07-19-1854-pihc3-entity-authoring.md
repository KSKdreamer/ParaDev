# PIHC3 entity binary authoring and strict starter builds

Date: 2026-07-19 18:54 +08

## Outcome

ParaDev can now author the binary half of a PIHC3 model entity without decoding real `.mesh` or `.anim` files as UTF-8 text. The desktop editor exposes an **Assets** tab for contained binary additions and exact replacements, while PIHC3's project-local entity family prevents an incomplete or wrong-type starter from reporting a successful build.

This extends the complete, byte-contracted `HOI4DEV_ENTITIES` migration from the previous checkpoint. The 184-file aggregate and its 182 build artifacts remain unchanged; the new work affects hand-authored starter behavior and GUI editing boundaries.

## Closed failures

- `.mesh` and `.anim` were incorrectly classified as code, so selecting a real `pdxasseti` binary could trigger a UTF-8 read failure. Both are now binary asset sources.
- Text, image, or asset drafts made before the first scaffold apply could be discarded when generated files replaced the draft entity. Those editors now stay visibly locked until the starter is written and refreshed.
- The basic starter referenced an animation without emitting `animations.asset`. It now creates `mesh.gfx`, `entity.asset`, and `animations.asset` below the canonical nested model root.
- A zero-binary starter previously built successfully despite referencing missing files. Targeted builds now emit `entity.missing_mesh_asset` and `entity.missing_animation_asset` until the exact referenced binaries exist.
- The validator previously accepted a configured path found in any asset slot. It now requires `mesh_file` in `meshes` and `animation_file` in `animations`; swapping a texture and mesh cannot bypass the guard.
- Editing or removing mutable provenance could previously disable the starter validator. A versioned authoring contract, exact template provenance, and any remaining singular asset reference now identify starters, while common PIHC3 entity tags and canonical model paths remain compatible with generic routed-source modules.
- Renamed text, header-only payloads, or truncated files could masquerade as `.mesh`/`.anim`. Required starter binaries now need the Paradox `pdxasseti` v2 container envelope plus the ordered mesh or animation structural sections verified against the 31 real PIHC model binaries.
- Valid metadata/assets could coexist with PDX definitions that referenced missing files or disagreed about mesh/state/animation names. Parsed starter PDX is now checked for exact file references and consistent cross-file links.
- Divergent advanced `default_state` and `animation` values previously made `entity.asset` point at a nonexistent mesh animation id. State references now use `default_state`, while the exported animation declaration continues to use the animation name.
- The basic form exposed `animation_file` as a basename while metadata used it as a full path. The redundant form argument is gone; the canonical path is derived from the animation name and advertised through the family contract.
- Six legacy `mesh.mesh` basenames and three `idle.anim` basenames make filename-only replacement unsafe. Generic drops never guess among duplicate matches; row-level replacement carries the exact source identity and path.
- Duplicate targets could silently discard bytes within one batch, across sequential drops, after a manual path edit, or across the Image and Assets tabs. Portable case, repeated-separator, Unicode-normalization, absolute/relative, and cross-operation aliases are now rejected in both the UI model and backend.
- Empty uploads, mismatched upload/target extensions, entity switches during a read, and unresolved multi-directory aggregate targets now preserve every pending choice or surface an explicit localized error. The pending queue is cumulatively capped at 32 files and 64 MB, and a later same-target selection wins even when an earlier file read finishes afterward.
- Project-contained symlinks could redirect an entity asset write into another module, including when an ancestor was swapped after validation. Source draft writes now use an atomic, no-follow descriptor chain on the current macOS/Linux release path, so a concurrent swap remains anchored to the already-open directory; unsupported platforms fail closed instead of falling back to a race-prone path. The backend also caps direct replacement requests at 64 files, 64 MB per file, and 128 MB total.
- Draft callbacks captured before **Apply** could modify an entity while its request was in flight, then be overwritten by the submitted snapshot. Per-entity synchronous in-flight guards now reject those stale mutations, and the editing body stays inert until every concurrent apply for that entity settles.
- Source text, image bytes, and asset bytes for one entity are submitted in one validated apply request, and written drafts are cleared only for paths reported by the backend.

## Novice workflow

1. Create **PIHC3 Basic Model Entity** with an ID and title, then click **Apply** once.
2. After refresh, edit the three generated PDX files or open **Assets**.
3. Add one exported `.mesh` and one `.anim`. Incoming filenames are mapped to the paths declared in `meta.yaml`; textures can be added alongside them.
4. Use the asset row's **Replace** action when changing an existing binary.
5. Build the entity. ParaDev blocks the build with exact missing-asset diagnostics until both required binary roles are satisfied.

With default values, the successful owner build emits exactly five files: three PDX definitions, `mesh.mesh`, and `idle.anim`. Texture placeholders still require the author to attach the exported model's actual textures before in-game rendering can be expected.

## Verification

- Standard ParaDev fast gate: 1,458 tests passed, one expected live-checkout skip, and two warnings in 343.06 seconds.
- Desktop Vitest: 56 files, 952 tests passed.
- Frontend TypeScript and production Vite build passed; the existing large-chunk warnings remain.
- PIHC migration-script suite: 188 tests passed.
- Project SDK regression file: 242 tests passed. Desktop backend and Tauri bridge files: 88 tests passed.
- Live starter/family/legacy acceptance against the PIHC worktree and latest local HeavenBase: 5 tests passed, 314 deselected. It covers incomplete and wrong-slot blocking, real-corpus binary structure and truncation, altered provenance, generic legacy compatibility, misplaced animations, wrong PDX references, divergent state/animation values, five-artifact success, registry capabilities, and legacy path preservation.
- Heaven-style scanner: the new `system/entity_family.py` passed with no banned imports.
- Black at 160 columns and Flake8 passed for the changed Python family and acceptance contract.

## Remaining release boundaries

- Native packaged-GUI acceptance is still required: first launch, project selection, create/apply/assets/build, keyboard/focus, and DMG presentation have not yet been exercised through the Tauri window.
- The last clean macOS ARM64 package is structurally valid but unsigned and unnotarized; public novice distribution still needs Developer ID signing, notarization, stapling, and Gatekeeper verification.
- The migrated aggregate is fully present and editable as path-preserving source and binary files, but its 134 legacy model/variant records are not yet split into 134 guided semantic modules.
- PDX definition editing is still a source editor after scaffold creation; higher-level mesh/state/animation forms remain a novice-authoring improvement.
- The corpus-backed structural check is not a complete `pdxasseti` parser. A specially crafted corruption after all required sections could still pass, and a future Paradox binary version needs evidence plus an explicit contract update.
- Descriptor-anchored source draft mutation depends on `dir_fd` and `O_NOFOLLOW`; Windows currently fails closed here. A Windows-native safe mutation primitive is required before Windows packaging can be called authoring-ready.
- The generic draft API validates every target before starting, but an unexpected filesystem failure during a later operation can still leave earlier text writes committed; a fully transactional mixed text/binary/removal apply remains a lower-probability hardening item.
- Division/OOB portability is the next stale personal-root migration boundary after this entity block is committed and pinned.
