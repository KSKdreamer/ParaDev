# PIHC3 Entity Parity Audit

Date: 2026-07-18 14:18 SGT

## Outcome

PIHC3 has broad native source ownership, but it does not yet have broad semantic parity with PIHC2. The current inventory contains 89 families, 18,038 modules, and 62,952 source rows. ParaDev exposes 47 top-level families in the desktop module browser and keeps 42 component families internal.

Only the PIHC2 country-leader trait slice has strict byte-for-byte parity evidence. Ideas have normalized PDX parity with documented localization deviations. Every other legacy domain is partial, path-preserved, or represented by aggregate source modules rather than beginner-editable records.

## Authoring Surface

- 45 creation templates cover 44 families and all report `authoring_ready`.
- `equipment_module`, `equipment_module_category`, and `special_project_reward` have no creation template.
- Existing module detail views expose source and localization slots as raw editors. Family-specific settings are not generally rendered as guided beginner forms.
- Focus and technology have diagram surfaces, but only focus exposes the complete tree command set.
- Component families are intentionally hidden from dynamic module navigation, even when they own source required to understand or complete an entity.
- Existing rendered and end-to-end coverage is fixture-heavy and does not exercise every live PIHC3 family/template pair.

## Legacy Domain Assessment

| PIHC2 domain | PIHC3 state | Parity assessment |
| --- | --- | --- |
| Traits | 139 trait modules plus support components | Full only for the country-leader slice: 417/417 PDX and localization artifacts are byte-exact. |
| Ideas | 390 idea modules plus assets/support | Near-complete normalized PDX parity; localization retains documented compatible differences. |
| Focuses | 28 aggregate focus-tree modules for 766 legacy focuses | Major partial: imported trees remain monoliths and individual focus content is not safely form-editable. |
| Events | 41 namespace modules for 867 legacy events | Partial: imported events remain namespace monoliths. |
| Decisions | 458 decision modules and 62 collections for 521 legacy records | Partial: category creation, merged-output parity, and beginner category editing are missing. |
| Characters | 250 character modules and portrait components | Partial: role templates, portrait regeneration, and animation workflows remain. |
| Countries | 67 country modules, 147 country components, and 1,110 flags | Partial: map, OOB, AI, setup, and portrait wiring remain fragmented. |
| Equipment | 167 equipment and 179 module/category records | Partial: designer GUI, inheritance, ship-module, and balance workflows remain. |
| Entities | One aggregate bundle for 134 legacy model/variant records | Major partial: no per-model or per-variant modules, assignment validation, or asset regeneration. |
| Random characters | Legacy evidence only | Missing editable random-character pool records. |
| Entity autodiffuse | Historical files only | No runnable migrated authoring pipeline. |
| Localization copies | One hidden component with 1,764 current rows | Paths are preserved, but the source is not reconstructed as a localization editor. |
| States and strategic regions | 902 state and 330 region modules | Partial: compiled text is editable; map/resource/province/weather validation is absent. |
| Remaining families | Native modules and/or component ownership | Structural coverage exists, but no whole-family semantic parity reviewer exists. |

The existing slow PIHC3 migration suite proves importer, ownership, metadata, source-slot, and representative artifact contracts. It is excluded from the default fast gate and must not be described as whole-family semantic parity. Dedicated parity reviewers currently exist only for ideas and traits.

## Dirty-Tree Risks Found

The current PIHC3 `v3.1` checkout contains several independent in-progress changes and must not be committed as one unit.

- `paradev.yaml` declares `0.2.3.006dev`, while the outer migration contract still requires `0.2.3`.
- C25/C44 naval OOB source changes leave scripted-effect and country-component metadata stale, which can mislead the generic editor even when runtime behavior is corrected.
- Generated Steam English markup closes a list early and splits the word “models”; the Chinese output contains an empty list.
- Synchronized dynamic-token metadata does not describe the current token file or `generator_complex`.
- The country-selector design note records visual QA as blocked and links to an ephemeral screenshot.
- The state-temperature modifier currently behaves as a one-shot startup correction; the first monthly recomputation replaces that adjusted value. Product intent must be confirmed before treating the contract as final.

## Priority Vertical Slice

The next entity migration should be a focus-tree vertical cut rather than another breadth-only importer pass:

1. Split the 28 imported tree monoliths into 766 collection-owned focus modules while preserving the same 28 output paths.
2. Add normalized PDX and localization parity against PIHC2.
3. Link migrated focus assets and retain missing-icon diagnostics.
4. Make title, description, cost, icon, prerequisites, mutual exclusions, completion reward, and position editable without raw PDX.
5. Make diagram Apply write canonical per-focus source rather than legacy metadata hints.
6. Add one fast representative contract, one full slow 766-focus parity contract, and a temporary-project native Tauri create/edit/build smoke.

This is the highest-leverage slice because focus is one of the largest PIHC2 domains, already has ParaDev's strongest graphical editor foundation, and currently has the clearest gap between apparent editability and canonical output ownership.

## Commit Partition Recommendation

Before the focus cut, preserve the existing dirty PIHC3 work as separate reviewable slices: outer REST/OpenAPI profile schema, C01 localization, country selector layout, Chinese event font, temperature localization, temperature startup adjustment, naval OOB, HoI4 1.19 building/token compatibility, and release README/version generation. Defer the release slice until its version contract and generated markup are corrected.
