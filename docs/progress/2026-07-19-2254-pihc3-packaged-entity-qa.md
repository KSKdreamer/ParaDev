# PIHC3 packaged Entity QA and migration-parity boundary

Date: 2026-07-19 22:54 +08

## Outcome

The packaged macOS ParaDev application can now open the selected PIHC3 checkout, load the direct `HOI4DEV_ENTITIES` aggregate on demand, preserve direct aggregate sources as editable files, attach real Paradox `.mesh` and `.anim` binaries, and complete a full GUI build with zero errors or diagnostics.

Two desktop fixes close the packaged-application failures found during this pass:

- `ad595b9e` (`fix(entities): load direct aggregate on demand`) replaces the empty Entity summary with a scoped browser payload when the Entity workspace opens. Ordinary modules remain catalog-only and do not pay the eager-loading cost.
- `8a069970` (`fix(entities): retain scaffold selection`) gives a newly applied scaffold its canonical browser identity, so refresh keeps the new module selected instead of jumping back to the aggregate.

Compiled migration parity is exact, but novice authoring parity is not complete. PIHC3 still flattens 134 PIHC2 model records, the type/tag assignment table, and the autodiffuse source pipeline into compiled aggregate output. Those are the next Entity migration boundary; the passing aggregate build must remain the golden reference while they are introduced.

## Packaged artifact

The current branch is `codex/tauri-backend-sidecar` at `8a069970`. The latest all-in-one ARM64 artifacts are:

- Application: `apps/desktop/src-tauri/target/release/bundle/macos/ParaDev.app`
- Disk image: `apps/desktop/src-tauri/target/release/bundle/dmg/ParaDev_0.1.0_aarch64.dmg`
- Bundled backend: 78,016,880 bytes; SHA-256 `e909e6001cce162a2c56ae61095982e155a772647e1a21b00d6e471ff76f56b8`
- Main executable: 4,029,424 bytes; SHA-256 `92cb64789033b2c205d806c9bec3d630195f24f6a847c6907505e7998ee8e547`
- DMG: 80,407,502 bytes; SHA-256 `2d502b3cac6acea8f01a2687ca6ea9c7a2ae699e9e125450a5e909cd5535f8b4`

The release build completed with the bundled-backend feature, and `hdiutil verify` passed every checksum with CRC `$1596C083`. A prior full run of the same packaging path also verified the DMG's `/Applications` link. The backend staged for Tauri and the backend embedded in the application have the same SHA-256.

The bundled `backend-info` command reports ParaDev `0.1.0.000dev`, HeavenBase `0.1.2.0`, Python `3.12.13`, macOS ARM64, and protocol `paradev.desktop.backend.v1`. Build-environment distribution metadata pins HeavenBase commit `7f4efc47fc794b52a58496b88cec2402289a1175`, which is the clean local HeavenBase `master`; installed HeavenBase source matches that checkout except for the intentionally uninstalled `resources/README.md` and bytecode.

The first full package in this QA pass was built at `ad595b9e` and exercised natively from a relocated application. The final `8a069970` package adds only the scaffold-selection identity fix; its full desktop and production-build gates passed before it was packaged.

## Native GUI acceptance

The application was copied out of the build tree and launched from:

`/private/tmp/paradev-entity-package-final.3RyE2F/ParaDev.app`

Process inspection confirmed that the running executable belonged to that relocated bundle. The selected project was a disposable clone, not the protected PIHC3 checkout:

`/Users/magolor/Projects/ParaDev/PIHC3-GUI-Smoke`

The clone intentionally differs only in smoke-test project identity/output settings and the new `GUI_SMOKE_ENTITY` sources. Nothing from this acceptance run was committed.

Observed native workflow:

1. Opening **Entity** replaced the cached summary with the direct aggregate: `1 object, 183 sources`.
2. The starter persisted as a second object with three generated PDX files plus metadata: `2 objects, 187 sources`.
3. The native asset picker selected a real `mesh.mesh` and `idle.anim`; the Assets tab mapped both to the canonical nested module targets and showed `2 ready`.
4. **Apply** wrote both binaries. Refresh reported `2 objects, 189 sources`, and the new object exposed `meta.yaml`, `animations.asset`, `entity.asset`, `mesh.gfx`, and **Resources**.
5. A full GUI build completed in 2 minutes 53 seconds at 100%, with `0` errors and `0` diagnostics. The Entity row reported `2 modules` and `190/190` source files processed.

The emitted object is at:

`/Users/magolor/Projects/ParaDev/PIHC3-GUI-Smoke/build/gui-smoke-mod/gfx/models/GUI_SMOKE_ENTITY`

It contains `animations.asset`, `entity.asset`, `idle.anim`, `mesh.gfx`, and `mesh.mesh`. The generated PDX definitions use the expected entity, mesh, state, animation, and file paths.

Both binary copies are exact:

| Role | Source, module, and built-output SHA-256 |
|---|---|
| Mesh | `34c6d27964ba9bb74760d0ced6055c93ef59f66ffb57ea23871939e5b24627ba` |
| Animation | `9c91bebcafcc4dca860aba3b2ce526fa43ffed973623b90342379d51a9bf1344` |

The native automation's observation of the initial scaffold **Apply** click was ambiguous because the accessibility tree became very large while the aggregate editor was open. The same packaged backend was therefore exercised directly with a dry plan followed by `write=true`; it created exactly the four planned starter sources, and a clean application relaunch loaded the result normally. This is not recorded as a no-write defect. The confirmed post-refresh selection defect was independently reproduced, fixed in `8a069970`, and covered by automated tests.

## PIHC2-to-PIHC3 parity audit

The game-facing corpus is complete:

- PIHC2 contributes 312 non-hidden Entity files: 134 `info.json` records, 173 static assets, and five legacy animation declarations.
- All 173 static assets match PIHC3 as an exact hash/size multiset: 42,796,593 bytes.
- All 182 PIHC3 compiled artifacts match the local compiled `PIHC_dev` baseline byte-for-byte: 44,357,882 bytes.
- The complete artifact-tree hash is `173c9cc1d39d7ff58746469853a3c68d9f346ac798401226dd26e8042fa6a007`.
- The focused Entity corpus contract passed all three tests.

The 134 records belong to six shared model roots:

| Owner | Records | Variants | Entity descriptors | Static assets |
|---|---:|---:|---:|---:|
| Airship | 68 | 67 | 68 | 70 |
| Mirror | 1 | 0 | 1 | 4 |
| Imperial | 38 | 37 | 114 | 51 |
| Resistance | 25 | 24 | 75 | 37 |
| Tank | 1 | 0 | 5 | 6 |
| Rifle | 1 | 0 | 1 | 5 |
| **Total** | **134** | **128** | **264** | **173** |

The remaining novice-authoring gaps are concrete:

- The 134 `info.json` records are embedded as contract evidence and compiled into one aggregate instead of being individually editable records.
- PIHC2's `entities.json` contains 244 types, 257 tags, and 605 ordered memberships. PIHC3 exposes only the generated 34,427-line asset with 8,607 clones, not an assignment-table editor.
- The autodiffuse authoring pipeline has 79 inputs/code files plus its dependent PNG sources. PIHC3 correctly preserves active DDS results, but not their editable generation inputs or action.
- Fourteen extra PIHC2 autodiffuse DDS files are stale derivatives with no current config or Entity variant and are intentionally omitted.

The safe migration target is six owning model modules, 134 editable child records, one structured ordered assignment object, and project-local autodiffuse inputs/action. New generators must shadow-compile against the current aggregate tree before the aggregate stops emitting.

## Verification

- Desktop Vitest after the lazy-scope fix: 958/958 passed; focused App suite: 57/57 passed.
- Desktop Vitest after the scaffold-identity fix: 958/958 passed; focused Entity/App coverage: 94 passed.
- TypeScript checking and the production Vite build passed after both fixes.
- Latest ARM64 Tauri package build passed with the bundled backend, and the DMG checksum verification passed.
- Focused PIHC3 Entity corpus contract: 3/3 passed against the latest local HeavenBase source path.
- Source and output hashes prove byte-exact `.mesh` and `.anim` handling through native selection, module mutation, and build.

## Safety invariant

The protected checkout at `ParaDev-3/projects/PIHC3` remains at exact HEAD `7a4efe41bf07084ffe8fe56c2ba2f158ea14527f`. Its pre-existing user changes and untracked files are unchanged. All native mutation and building used the disposable `PIHC3-GUI-Smoke` clone.

## Remaining release boundaries

- Introduce and shadow-verify the 134 editable model records, structured assignments, and autodiffuse sources/action before claiming full PIHC2 novice-authoring migration.
- The macOS package is ad-hoc/unsigned and not notarized. Public distribution still needs Developer ID signing, notarization, stapling, and Gatekeeper verification.
- Full sidecar builds are not yet reproducible across identical Python-source inputs: separate successful builds produced different sidecar hashes despite reproducible-mode packaging. This needs isolation before release provenance can be considered deterministic.
- Very large aggregate source editors stress the native accessibility tree and can time out UI automation. The normal visible workflow remained responsive, but virtualization or reduced accessibility-tree surface is worth profiling.
- Windows safe binary mutation remains fail-closed until an equivalent to the current descriptor-anchored, no-follow POSIX path is implemented.
