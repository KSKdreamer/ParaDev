# HOI4 Domain And Entity Model

Status: draft

## Domain Goal

ParaDev should model HOI4 modding as structured authored content plus deterministic generated artifacts. PDX files, localization, images, map files, and game entities should be connected by explicit ownership and validation contracts.

## PDX File Families

A HOI4 project includes at least these file roots:

| Root | Typical contents | ParaDev ownership |
| --- | --- | --- |
| `common/` | game systems, entities, rules, AI, units, technologies, decisions | generated and source-owned by entity compilers and helper libraries |
| `events/` | event namespaces and event files | event collection compiler |
| `history/` | country, state, unit, and setup history | country, map, and scenario compilers |
| `localisation/` | game localization YML | localization compiler |
| `gfx/` | DDS/TGA/asset resources | asset pipeline and game-specific exporters |
| `interface/` | GUI, GFX sprite declarations, panels | asset and UI compilers |
| `map/` | provinces, states, strategic regions, terrain, heightmap | map subsystem |
| `music/`, `sound/` | music and sound declarations | asset/static pipeline |
| `descriptor.mod` and launcher `.mod` | mod metadata | project build layer |

The parser layer should understand PDX syntax broadly. The game package layer should understand the meaning of specific paths.

## Entity Contract Shapes

HOI4 entities should not all share one artificial shape. Use these contract classes.

| Contract shape | Examples | Key requirement |
| --- | --- | --- |
| Atomic standalone | achievements, modifiers, many traits | one unit can compile independently |
| Atomic with optional collection | ideas, intel agencies | unit output plus optional grouping or graph checks |
| Atomic in required collection | focuses, events, decisions, technologies, doctrines | final output depends on collection assembly |
| Composite asset-heavy | characters, countries, models | one source object owns script, localization, many assets, and sidecars |
| Helper library | scripted effects, triggers, localisation, on-actions | reusable symbols with dependency checks |
| Map/world data | provinces, states, strategic regions | geometry, IDs, colors, and history need specialized validators |
| Project-only custom | PIHC inventory items, superevents, state lores | project extension until reusable elsewhere |

## Entity Family Catalog

The PIHC2 counts below come from legacy `resources/**/info.json` inventory and should be treated as migration scale evidence, not current target-state schema.

| Family | PIHC2 count | Source prefix or root | Contract shape | Target notes |
| --- | ---: | --- | --- | --- |
| achievements | 49 | `ACHIEVEMENT_*` | atomic standalone | strict icon, localization, and condition validation |
| balance of power | 8 | `bops/` | collection-aware | model sides, ranges, modifiers, icons |
| characters | 250 | `CHARACTER_*` | composite asset-heavy | roles, country binding, portraits, animations |
| countries | 67 | `COUNTRY_*` or tag folders | composite asset-heavy | tag, history, colors, flags, AI, units, names |
| decisions | 521 | `DECISION_CATEGORY_*` and `DECISION_*` | required collection | category owns grouped output and validation |
| doctrines | 94 | `DOCTRINE_*` | required collection | post-1.17 doctrine system needs dedicated semantics |
| 3D entities/models | 134 | `entities/` | composite asset-heavy | starter covers per-module mesh/entity shell; mesh/texture/animation copying, aggregate mesh GFX, unit assignment, and import parity remain |
| equipment | 297 | `ARCHETYPE_*`, `EQUIPMENT_*`, `MODULE_*`, `UPGRADE_*` | mixed | split archetypes, equipment, modules, upgrades |
| events | 867 | event spaces and `EVENT_*` | required collection | namespace/file grouping, scheduling, pictures |
| focuses | 766 | `FOCUS_TREE_*`, `FOCUS_*` | required collection with layout | tree assembly, prerequisites, positions |
| idea categories | 39 | category metadata | collection/helper | starter covers category-law shell; nested idea aggregation, legacy level ordering, icons, and import parity remain |
| ideas | 390 | `IDEA_*` | atomic with optional collection | icons, law chains, categories, localization |
| intel agencies | 9 | `INTEL_AGENCY_*` | optional collection | icons, upgrades, graph checks |
| inventory items | 61 | PIHC custom | project-only custom | PIHC extension; starter covers effect/loc helpers, full GUI/icon parity remains |
| localization | many | `locs`, `**/*.loc`, YML | cross-cutting | key ownership, translation, termbase |
| modifiers | 7 | `MODIFIER_*` | atomic standalone | dynamic/static modifier references |
| opinions | 428 | opinion modifiers | helper/domain | diplomatic opinion records and localization |
| special projects | 43 | `SP_*`, rewards | mixed | project/reward split, icons, effects |
| state lores | 2 `info.json`, 79 lore folders | PIHC custom | project-only custom | starter covers scripted-localisation/on-action shell; aggregate import, alternate triggers, and multi-language parity remain |
| states | not counted by `info.json` | `history/states`, map data | map/world data | owner, cores, resources, buildings, provinces |
| strategic regions | not counted by `info.json` | `map/strategicregions` | map/world data | air/naval regions, province lists |
| superevents | 14 | PIHC custom | project-only custom | starter covers event/news shell; GUI, music, images, scripted localization parity remains |
| technologies | 300 | `TECHNOLOGY_*` | required collection with layout | tech folders, prerequisites, UI positions |
| traits | 139 | `TRAIT_*`, subtypes | subtype cluster | leader, commander, operative, country-leader differences |

## Source Folder Baseline

Recommended entity folder shape:

```text
modules/<type>/<MACHINE_NAME> - optional note/
  def.txt
  main.loc
  icon.png
  assets/
  meta.yaml
```

The active source contract is defined in `docs/goals/final-architecture.md`. New sources should use typed parent folders and deduce the module object id from the folder machine name. Compatibility aliases may read old names such as prefixed folders, `def.txt`, `locs.txt`, and `info.json`, but new docs should teach the new source contract. Migration importers can convert legacy folders into the new shape.

Recommended collection shape:

```text
modules/focus_tree/C01_MAIN/
  meta.yaml
  def.txt
  focuses/
    C01_START/
      def.txt
      main.loc
      icon.png
    C01_BRANCH/
      def.txt
      main.loc
```

Legacy importers may still read this older shape:

```text
FOCUS_TREE_C01_MAIN/
  meta.yaml
  def.txt
  FOCUS_C01_START/
    def.txt
    main.loc
    icon.png
  FOCUS_C01_BRANCH/
    def.txt
    main.loc
```

For simple families, the collection can be implicit. For graph and grouped-output families, collection identity must be explicit or deterministically inferred with diagnostics.

## Metadata Contract

Every family should publish:

- allowed metadata keys;
- types and default values;
- source slots;
- output artifacts;
- required localization keys;
- asset size and format policy;
- ID resolution policy;
- validation stages;
- editor payload schema.

Shared metadata candidates, aligned with the final architecture:

| Key | Meaning |
| --- | --- |
| `type` | module family identifier when it cannot be inferred from path |
| `title` | human-facing label for UI and search |
| `comment` | optional natural-language notes for developers and future agent generation |
| `tags` | search and editor tags |
| `game_id` | optional explicit game-facing id |
| `scope` | optional source grouping or project-domain scope |
| `collection` | collection id |
| `owner` | source owner or country tag |
| `priority` | deterministic ordering hint |
| `since` | game or mod version introduced |
| `settings` | family-specific compiler settings such as `icon_size` and `icon_fit` |

Family-specific keys must remain family-local.

## Build Stages

Use a stage model that can handle both simple and complex families:

1. discover source files and folders;
2. parse PDX, localization, metadata, and assets;
3. normalize into typed records;
4. aggregate collections;
5. validate units, collections, references, and outputs;
6. compile game-ready artifacts;
7. emit manifests and diagnostics;
8. update HeavenBase indexes.

The current stale ParaDev stage names (`load`, `transform`, `export`) are useful but too narrow. The restart should make collection, validation, and index update explicit.

## Localization Model

Localization should support:

- `.loc` or `.loc.txt` human-authored source;
- HOI4 YML read/write;
- per-language output folders and `replace`;
- scoped keys such as `@` or `@_desc` expanding from the entity id for
  entity-local `main.loc`;
- language aliases such as `en`, `zh`, `ru`;
- termbase-constrained translation;
- exact key lookup, prefix lookup, fuzzy search, and paragraph scanning;
- translation review state and provenance;
- LSP/editor diagnostics for missing keys, duplicate keys, and stale generated YML.

HeavenBase should store `loc-entry`, `loc-key`, `term-concept`, and `term` rows. The source files remain the Git-authored truth.

## Asset And Wand Image Utilities

The restarted asset subsystem should preserve the useful behavior of the current Wand/ImageMagick pipeline.

Core capabilities:

- load and save PNG, JPG, JPEG, BMP, DDS, TGA, GIF, and WEBP where supported;
- infer image paths with extension priority such as PNG, DDS, TGA;
- save DDS with explicit compression and mipmap policy;
- save TGA with the HOI4 vertical flip convention;
- flatten alpha when producing RGB-like outputs;
- create blank canvases;
- inspect dimensions, colorspace, alpha, compression, and format.

Transforms:

- resize by ratio;
- `cover` fit with crop;
- `contain` fit with transparent extension;
- crop;
- extend;
- rotate;
- shift;
- vertical and horizontal flip.

Color operations:

- grayscale;
- replace color with fuzz;
- color key to alpha;
- colorize/tint;
- gamma;
- brightness and contrast;
- color transfer.

Compositing:

- overlay;
- multi-image composite;
- alpha mask;
- shadowed/two-frame strips for UI effects;
- grayscale or darkened variants for achievements and disabled icons.

Video:

- sample frames from MP4 or other OpenCV-supported video;
- produce horizontal frame strips;
- split and merge strips;
- use FFmpeg/OpenCV only through guarded optional dependencies.

Caching:

- source hash based invalidation;
- deterministic cache keys;
- derived DDS plus JSON metadata;
- cache stats and clear commands.

Dependency policy:

- `wand` plus ImageMagick remains the preferred high-quality image engine for DDS/TGA-heavy HOI4 workflows.
- The package must import cleanly when ImageMagick is missing.
- Public image operations should fail with clear installation and feature messages.
- Pillow can be considered for lightweight previews, but not as the canonical DDS writer unless proven better.

HeavenBase role:

- store source asset metadata;
- store derivative metadata and provenance;
- store generated-media prompts and review state;
- do not store large image bytes as ordinary table rows by default.

## Map And World Model

The map subsystem should eventually support:

- province bitmap and province definitions;
- state definitions and state history;
- strategic regions;
- terrain, heightmap, rivers, supply, buildings, resources, victory points;
- country ownership and cores;
- GUI selection of provinces and states;
- generated code snippets from selected IDs;
- validation of province-state-region consistency;
- diffing map data against vanilla and PIHC baselines.

Suggested HeavenBase entities:

- `map-province`;
- `map-state`;
- `strategic-region`;
- `map-layer`;
- `map-selection`;
- `state-history`;
- `map-diagnostic`.

The first GUI should browse and select. Editing and writeback should wait for stable schemas and validation.

## HOI4 Reference Database

The knowledge layer should ingest and version:

- effects;
- triggers;
- modifiers;
- scopes;
- scripted helper examples;
- entity templates;
- common output paths;
- patch notes and game-version deltas;
- curated vanilla snippets.

Implementation sources:

- current game files from a configured local HOI4 install;
- Paradox wiki pages when retrievable;
- official patch notes and developer diaries;
- internal migration findings.

Every reference row needs source provenance and freshness metadata. Agents should cite or surface provenance before writing mechanics-sensitive content.

## Editor Payloads

Editor payloads should be built from the same normalized records and manifests:

- `focus-tree.view.v1`;
- `map-selection.view.v1`;
- `loc-scan.view.v1`;
- `entity-form.schema.v1`;
- `asset-preview.view.v1`;
- `build-diagnostics.view.v1`.

Each payload should be versioned, deterministic, and backed by tests.
