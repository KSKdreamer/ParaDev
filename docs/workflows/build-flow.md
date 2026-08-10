# Build Flow

Status: active workflow

Date: 2026-06-07

Purpose: show the smallest user-facing build path for the current SDK and CLI, using the minimal demo project.

## Mental Model

The beginner model is:

1. A project has source roots.
2. Source roots contain modules under `modules/<family>/<module>/`.
3. A build profile discovers modules, plans artifacts, and optionally writes outputs and manifests.

The current default profile for `game: hoi4` is a scaffold. It proves project-owned descriptor `.mod` metadata, collection-owned focus, event, and decision PDX output, plus module-owned localization and static-copy outputs; full HOI4 focus tree layout compilation is still future work.

## Create A Starter Project

Create the smallest buildable HOI4 project from an empty folder:

```bash
rtk uv run paradev new projects/starter-mod --title "Starter Mod" --json
```

The command writes `paradev.yaml`, creates `src/`, the default output root, `.paradev/.cache/build/`, and one `modifier` module under `src/modules/modifier/<project_id>_starter_modifier/`. For HoI4 on macOS, the default output root is `~/Documents/Paradox Interactive/Hearts of Iron IV/mod/<project_id>/`; set `output_root: build/mod` for project-local generated output. The starter uses only the default HOI4 profile, so a new user can immediately run:

```bash
rtk uv run paradev build projects/starter-mod --emit-artifacts --emit-manifests --json
```

The default HOI4 profile plans two project-owned `mod_descriptor` artifacts for every project build. `descriptor.mod` is written under the output root, while `.paradev/.cache/build/launcher/<project_id>.mod` is a launcher preview that includes `path="<absolute output_root>"`. When the output root is inside the HoI4 user mod folder, ParaDev also syncs `<project_id>.mod` beside it for the launcher.

To inspect and create additional source modules without learning the folder contract by hand, use authoring templates:

```bash
rtk uv run paradev templates projects/starter-mod --json
rtk uv run paradev authoring-path projects/starter-mod module idea GER_industry_spirit --json
rtk uv run paradev authoring-plan projects/starter-mod module idea GER_industry_spirit --json
rtk uv run paradev scaffold projects/starter-mod hoi4:idea/basic GER_industry_spirit \
  --value "title=German Industry Spirit" \
  --value "description=Industrial production spirit." \
  --json
rtk uv run paradev scaffold projects/starter-mod hoi4:idea/basic GER_industry_spirit \
  --value "title=German Industry Spirit" \
  --value "description=Industrial production spirit." \
  --write \
  --json
```

`authoring-path` returns a read-only `paradev.sdk.authoring_path.v1` payload with the resolved `root`, project-relative path, selected source root, folder template, and the future `module_id` for module targets. `authoring-plan` returns `paradev.sdk.authoring_plan.v1`, nests that same path payload, and adds registry-owned expected source-slot rows with slot names, match patterns, loader kinds when known, required flags, suggested concrete paths for exact slot matches, current matched paths, slot status, and any family-level `default_asset` metadata for that logical slot. Status is one of `empty`, `missing`, `satisfied`, or `diagnostic`; the payload index includes `status` so tools can jump to missing or diagnostic rows quickly. `Project.authoring_path(...)` and `Project.authoring_plan(...)` delegate to reusable build-layer helpers, and lower-level adapters can call `authoring_view(...)` to render source-root/template context from explicit project paths. REST/OpenAPI exposes the same reads as `/projects/templates`, `/projects/authoring-path`, and `/projects/authoring-plan`, plus write-capable `/projects/scaffold`; the MCP surface contract exposes `project_templates`, `project_authoring_path`, `project_authoring_plan`, and write-capable `project_scaffold` tools. `scaffold` dry-runs by default and returns the same JSON-safe `paradev.sdk.module_scaffold.v1` payload as the Python SDK, with a nested `authoring_plan` showing the source-slot status for the target root. This gives CLI scripts, GUI clients, MCP tools, and future importer clients one generic creation contract instead of hard-coding one command per module family. The `templates` payload includes `source_roots` rows with `path`, `relative_path`, and `default` fields. Each template row includes typed `args`, GUI-ready `form.fields`, a `renderer` value of `files` or `python`, the physical-folder format `directory`, `default_assets` for its family, and `authoring_ready` so tools know whether its family is registered before offering scaffold writes. `directory` defaults to `{object_id}`; project-local templates can opt into formats such as `{object_id} - {title}` without changing logical identity. Scaffold and batch module plans keep `object_id` and `module_id` logical and add the resolved physical `folder_name`. Class-level default assets are advertised for form previews and editor affordances, but they are not written into the target module unless a user explicitly authors an instance asset. Rows that are not ready include `diagnostic_codes: ["template.unknown_family"]`, and `Project.scaffold_module(...)` rejects them before rendering. The template `index` maps `id`, `family`, `source`, `authoring_ready`, and `diagnostic_code` to row numbers. Those same fields are exact filters on `Project.templates(...)`, `paradev templates`, and `/projects/templates`; returned indexes are rebuilt for the filtered table. Projects with multiple configured `source_roots` can pass `--source-root <root>`; the value resolves relative to the project root and must match a manifest source root.

Scaffold resolves an existing physical folder by logical id before choosing a
new rendered name. One unique match is reused, while aliases and case- or
NFC-equivalent collisions block the plan. Existing-content idempotence ignores
the reserved module-local `.paradev/` system metadata directory. Fresh
scaffolds do not create importer provenance there. Module rename changes the
logical id while preserving a readable suffix.

SDK callers can create the same starter project before loading or building it:

```python
from paradev.sdk import Project

project = Project.create("projects/starter-mod", title="Starter Mod")
result = project.build(emit_artifacts=True, emit_manifests=True)
assert (project.output_root / "descriptor.mod").is_file()
assert (project.build_root / "launcher/starter_mod.mod").is_file()
```

The HOI4 profile also supports the first simple PDX-plus-localization families and the first asset family:

- `modules/event/<object_id>/` writes collection-owned `events/<collection_id>.txt`, or `events/<object_id>.txt` when no collection is set
- `modules/decision/<object_id>/` merges authored decision entries into collection-owned `common/decisions/<collection_id>.txt`
- `modules/idea/<object_id>/` writes `common/ideas/<object_id>.txt`, localization, and an optional idea icon
- `modules/modifier/<object_id>/` writes `common/modifiers/<object_id>.txt`
- `modules/opinion_modifier/<object_id>/` writes `common/opinion_modifiers/<object_id>.txt`
- `modules/trait/<object_id>/` routes by `settings.subtype`

Trait modules require `meta.yaml` to set `settings.subtype` to `country_leader`, `unit_leader`, or `scientist`. The profile writes those traits to `common/country_leader/<object_id>.txt`, `common/unit_leader/<object_id>.txt`, or `common/scientist_traits/<object_id>.txt` respectively. These paths and the decision output split were checked against the local HOI4 install on 2026-06-06: `launcher-settings.json` reports `rawVersion` `1.18.2.0`, decision entries are under `common/decisions/*.txt`, and category definitions are under `common/decisions/categories/*.txt`.

Idea modules use the same `def.txt` and `**/*.loc` model as simple families, plus a narrow icon slot:

```text
src/modules/idea/GER_industry_spirit/
  meta.yaml
  def.txt
  main.loc
  icon.dds
```

The HOI4 profile writes the idea PDX file to `common/ideas/<object_id>.txt`, writes localization to `localisation/<language>/<object_id>_<language>.yml`, copies `icon.png`, `icon.dds`, or `icon.tga` to `gfx/interface/ideas/idea_<object_id>.<ext>`, and emits `interface/paradev_idea.gfx` with `GFX_idea_<object_id>` pointing at the copied icon. Here `<object_id>` means the game-facing id used by the generic artifact templates: `game_id` when present, otherwise the inferred folder object id. The authored PDX must declare the idea key as `<object_id>` and, when an icon is authored, must keep its game-facing `picture = <object_id>` value aligned with that icon and sprite filename convention. If a module authors localization, each language must include `<object_id>` and `<object_id>_desc`. Missing or mismatched idea ids, localization keys, icon picture values, and duplicate sprite names produce blocking diagnostics anchored to source files. Copied PNG, DDS, and TGA sources expose hash, byte size, media type, format, width, and height in artifact metadata for later asset previews and validation. This first asset-family proof does not convert image formats yet. These paths and sprite names were checked against the local HOI4 install on 2026-06-07: `rawVersion` is `1.18.2.0`, idea script files live under `common/ideas/*.txt`, idea icon files live under `gfx/interface/ideas/*.dds`, and `interface/ideas.gfx` declares `GFX_idea_*` sprites with `gfx/interface/ideas/idea_*.dds` texture files.

Collected event modules block duplicate `country_event`/`news_event` ids and event ids whose namespace prefix does not match the collection id. Diagnostics are anchored to the source `id` span when the PDX parser provides one.

Decision modules should wrap their decision entry in the category block named by `collection`:

```pdx
GER_industry = {
	GER_decision_one = { icon = generic_industry }
}
```

Collection descriptors can also provide the category definition at `collections/decision/<collection_id>/def.txt`:

```pdx
GER_industry = {
	icon = generic_industry
	picture = GFX_decision_cat_picture_generic
}
```

Collection descriptors can also own category localization in root-level `**/*.loc` files:

```ini
[en.GER_industry]
German Industry

[en.GER_industry_desc]
Industrial mobilization decisions.
```

The HOI4 profile writes the PDX descriptor to `common/decisions/categories/<collection_id>.txt`, writes collection localization to `localisation/<language>/<collection_id>_<language>.yml`, then merges all decision entries from the same collection into one top-level category block under `common/decisions/<collection_id>.txt`. A decision module without `collection` reports `decision.missing_collection` instead of silently dropping output. Duplicate decision ids report `decision.duplicate_id` at the duplicate decision key span. If a source uses a top-level category key that does not match `collection`, the build reports `decision.category_mismatch` at that category key span; collection descriptor key mismatches report `decision.category_descriptor_mismatch`. If collection localization is authored, each language must include `<collection_id>` and `<collection_id>_desc`, otherwise the build reports `decision.category_missing_localization`.

## Inspect Build Summary

To check the current build size and blocked status without printing every manifest row:

```bash
rtk uv run paradev summary demos/assets/projects/minimal --json
```

SDK callers can use the same dry-run view:

```python
from paradev.sdk import Project

payload = Project.load("demos/assets/projects/minimal").summary()
```

The payload uses `paradev.build.summary.v1` and includes module, collection, dependency, artifact, diagnostic, error, and blocked counts. It is projected from a dry build, so it does not write `.paradev/.cache/build/summary.json`; use `paradev build --emit-manifests` when the manifest files should be materialized. Dry and emitted builds may atomically refresh hidden parsed-source entries under `.paradev/cache/source-families/` and finalized plans under `.paradev/cache/artifact-plans/`. Parsed-source entries carry a checksummed sorted per-file digest inventory. Trusted local files can reuse a digest only on exact safe metadata matches; ambiguous files, unknown filesystems, symlinked/cross-device topology, corruption, and races use full hashing, reparsing, or cache bypass. A hit is authorized by one final source fingerprint after the bounded payload is decoded. The plan signature covers complete source-cache signatures, copy inputs, Registry and compiler implementation, project/profile inputs, runtime dependencies, and extension-declared external state. Missing, stale, corrupt, oversized, or unwritable entries fall back to normal work; a postprocessor that cannot safely fingerprint external inputs disables plan reuse. Full builds always replan and refresh caches. Cache hits still resolve the requested target, calculate its safe publication closure, validate the retained artifact ledger, publish transactionally, and emit canonical manifests. On an exact finalized-plan hit, ParaDev may retain canonical manifest bytes through a hidden receipt under `.paradev/cache/manifest-publications/`. The receipt binds the plan signature, projector implementation, complete manifest inventory, and every retained file SHA-256. Missing, stale, corrupt, incomplete, or unwritable receipts fall back to normal projection; an externally edited manifest is repaired automatically. All three cache folders are disposable hidden derived state, not authored metadata or build manifests.

## Inspect All Manifests

To inspect the complete manifest set without writing `.paradev/.cache/build/*.json` files:

```bash
rtk uv run paradev manifests demos/assets/projects/minimal --json
```

SDK callers can use:

```python
from paradev.sdk import Project

payload = Project.load("demos/assets/projects/minimal").manifests()
```

The payload uses `paradev.build.manifests.v1` and nests every current build manifest by file name, including `modules.json`, `collections.json`, `artifacts.json`, `dependencies.json`, `diagnostics.json`, `assets.json`, `sprites.json`, `localization.json`, `sources.json`, `source-map.json`, and `summary.json`. Use it when a script, GUI, MCP tool, or test needs the whole build inspection bundle from one dry run. Use `paradev build --emit-manifests` only when those payloads should be written to the project build root.

Adapter-style SDK callers can dispatch read-only inspection requests through `Project.inspect(kind, **filters)` instead of duplicating command routing. The supported kinds are discoverable from `Project.inspections()` or `paradev inspections`; static adapter registration can use `get_project_inspection_contract()` before loading a project. The kinds currently include `inspections`, `summary`, `manifests`, `modules`, `collections`, `artifacts`, `localization`, `source-slots`, `sources`, `assets`, `sprites`, `diagnostics`, `source-map`, `dependencies`, `build-graph`, `build-explain`, `catalog-preview`, `catalog-query`, and `families`. The dispatcher forwards filters to the matching SDK method and ignores `None` values. `get_cli_contract()["inspection_contract"]`, MCP `project_inspect.inspection_contract`, and OpenAPI `/projects/inspect` `x-paradev-inspection-contract` expose the same static kind/filter metadata.

Filtered manifest inspections are owned by the build layer once a caller has a `BuildResult`: `paradev.build.summary_view(...)`, `manifests_view(...)`, `modules_view(...)`, `collections_view(...)`, `artifacts_view(...)`, `localization_view(...)`, `assets_view(...)`, `sources_view(...)`, `sprites_view(...)`, `diagnostics_view(...)`, `source_map_view(...)`, and `dependencies_view(...)` all return SDK-compatible payloads and rebuild indexes after applying filters where relevant. `Project` uses those helpers internally, so GUI, MCP, REST, importer, and compiler tests can share one filtering contract instead of reimplementing SDK-private row predicates.

## Inspect Families

To inspect the registered build families and artifact writers for a profile:

```bash
rtk uv run paradev families demos/assets/projects/minimal --json
rtk uv run paradev families demos/assets/projects/minimal --family idea --source-slot icon --artifact-type sprite_gfx --json
```

SDK callers can use:

```python
from paradev.sdk import Project

payload = Project.load("demos/assets/projects/minimal").families()
```

The payload uses `paradev.build.families.v1` and lists the profile authoring contract, each family, compiler kind, compiler stages, metadata contract, localization contract, asset contract, source slots, selected sprite slots, collection descriptor source slots, artifact templates, derived output contracts, registered routed settings such as `settings.subtype`, and artifact writer types. System-owned publication migrations are intentionally absent from family rows: they belong to the extension's hidden Registry descriptor, not to the compiler or user-facing authoring contract. The top-level `authoring` block lists valid source roots plus the default `modules/{family}/{object_id}` and `collections/{family}/{collection_id}` folder templates; a project-local scaffold template may override the module folder name through its `directory` format. Call `Project.authoring_path(...)` or `paradev authoring-path` to resolve one concrete module or collection root from that contract. Family `outputs` rows list planned artifact type, template key, template text, owner kind, target root, and route or sprite-slot context where applicable. The top-level `index` maps family id, compiler kind, source slot, collection descriptor source slot, sprite slot, routed route id, output artifact type, and artifact writer type to row numbers in the returned `families` or `writers` lists; `output_artifact_type` points at family rows, while `artifact_type` points at writer rows. `Project.families(...)` and `paradev families` delegate to the reusable build-layer wrapper `paradev.build.families_view(...)` and accept exact filters for `family`, `kind`, `source_slot`, `collection_source_slot`, `sprite_slot`, `route`, and `artifact_type`; filtered payloads rebuild their index against the returned rows. Source slots include the slot name, match pattern, optional loader `kind`, and `required`, `many`, `regex`, and opt-in `shared` flags. The `stages` list uses the build pipeline names such as `discover`, `load`, `normalize`, `aggregate`, `check`, and `emit`, so SDK, GUI, MCP, and script clients can explain what a family participates in without inspecting Python methods. The metadata contract lists accepted top-level metadata keys plus settings keys, required flags, and any allowed values; collection-owning families apply those family metadata keys to both module `meta.yaml` and collection descriptor `meta.yaml` or `collection.yaml`, and the shared `comment` key is accepted for optional developer notes. Malformed or non-mapping module metadata reports `metadata.invalid_yaml`; unreadable module metadata reports `metadata.unreadable_source`. Malformed or non-mapping collection descriptor metadata reports `collection_metadata.invalid_yaml`; unreadable collection descriptor metadata reports `collection_metadata.unreadable_source`. Collection descriptors that author `settings` are checked against their own family's declared `settings_values`; `required_settings` remains the module/source-side requirement. The localization contract lists required key templates such as `{object_id}` and `{object_id}_desc` for families that validate authored localization. The asset contract lists per-slot copy asset constraints such as allowed formats, width, and height for families that opt into asset validation, plus `defaults` entries for abstract family-level fallback assets. These defaults are normalized with title, source, path or asset id, editable flag, and `injected: false`; they are for discovery and override management, not automatic source-folder writes. Collection descriptor settings, localization, and asset contracts are scoped to the descriptor's family, so separate families may reuse setting names and slot names with different allowed values. GUI, MCP, and script clients should use this profile-owned payload instead of hard-coding HOI4 family routes, metadata keys, localization keys, asset dimensions, default assets, sprite slots, collection descriptor filenames, compiler stages, output templates, artifact writer types, or module folder rules.

To inspect expected versus found source slots for discovered modules and collection descriptors:

```bash
rtk uv run paradev source-slots demos/assets/projects/minimal --json
rtk uv run paradev source-slots demos/assets/projects/minimal --status missing --json
```

SDK callers can use:

```python
slots = Project.load("demos/assets/projects/minimal").source_slots(status="missing")
```

The payload uses `paradev.build.source-slots.v1` and joins the selected registry's slot contracts with the current dry build's discovered source rows and diagnostics. Each row has an owner (`module_id` or `collection_id`), family, source root, slot name, match pattern or `matches` list for repeated declarations, `required`/`many`/`regex` flags, optional loader, matched paths, source statuses, diagnostic codes, and a slot-level status: `satisfied`, `missing`, `empty`, or `diagnostic`. Exact slot rows also include `suggested_relative_paths` and `suggested_paths`, so tools can answer "what files should exist here?" and "where should I create the missing exact file?" without duplicating the join between `families()` and `sources()`. The SDK delegates this payload to the reusable build helper `paradev.build.source_slot_status(...)`, so new surfaces should call the SDK dispatcher and new build-level tests can exercise the helper directly. Use `sources` for actual loaded file rows and `source-map` for artifact-to-source traceability.

Family authors may declare family-specific source slots on the registered family. During `Project.build(...)`, discovery uses the selected registry: explicit family slots override profile defaults, while families without explicit slots keep the profile default module layout. Collection-owning families may also declare `collection_source_slots` for descriptors under `collections/<family>/<collection>/`; otherwise descriptor discovery keeps the default `def.txt` plus `**/*.loc` layout. Repeated declarations with the same slot name merge into one deterministic, de-duplicated path list, which lets families combine root-level and nested localization patterns under a single `loc` slot. If the merged logical slot still has `many=False`, more than one matched path reports `slot.multiple_matches` and keeps the first deterministic path. If one source file matches multiple logical slots, every owning slot must set `shared=True`; otherwise discovery reports `slot.source_collision`. Exact and glob slot matches must be relative and stay under the module or collection descriptor root; manifest and Python-backed family validation rejects parent traversal such as `../`, while direct SDK matching reports `slot.invalid_match`. Source slot regex patterns are compiled during project load or registry registration, so malformed patterns fail before discovery starts; direct SDK matching reports malformed regexes as `slot.invalid_regex` diagnostics. For generic collection-source families, descriptor PDX entries are prepended to member module PDX entries in the collection artifact and stay visible as descriptor inputs in source-map payloads. Descriptor localization entries use the same `loc_path_template`, rendered with the collection id as `object_id`, and produce collection-owned localization artifacts with source-map inputs. Malformed legacy `.loc` headers or entries report `loc.invalid_line` or `loc.missing_language`; YAML-shaped localization remains readable for compatibility and reports `loc.invalid_yaml`, `loc.invalid_file`, `loc.invalid_language`, or `loc.invalid_entry` when malformed. Descriptor copy sources use the same `copy_path_template`, rendered with the collection id as `object_id`, and produce collection-owned static copy artifacts with hash metadata. Descriptor-owned PDX, localization, and copy artifacts can be emitted before any member modules exist, and descriptor localization/copy outputs do not require a descriptor PDX source, so users can stage collection scaffolds without adding placeholder modules. Custom slot names can set `kind="pdx"`, `kind="loc"`, or `kind="copy"` so the generic loaders parse them without requiring global slot-name conventions. Generic simple, routed, and collection families can also declare `required_loc_keys`; if a module or collection descriptor authors localization, each language must include the rendered keys or the build reports `<family>.missing_localization`. Required localization templates support `{family}`, `{module_id}`, `{collection_id}`, and `{object_id}`; collection descriptors render `{object_id}` and `{collection_id}` as the collection id. Families can also declare `asset_constraints`; if a matched module or collection descriptor copy source violates its format or dimensions, the build reports `<family>.asset_format`, `<family>.asset_dimensions`, or `<family>.asset_metadata_missing`. For module sources, per-key `settings_normalizers` run before validation and artifact planning so routed settings and manifests use the canonical value.

Generic simple-source families can also aggregate selected copied asset slots into a sprite declaration artifact. The family keeps the copied texture path as the sprite `texturefile`, uses `sprite_name_template` for the `SpriteType.name`, and writes one `sprite_gfx_path_template` artifact with source-map inputs for every contributing asset. This keeps authoring simple: the source module owns an image slot, while the family owns whether that image also needs an interface sprite declaration.
If two selected copied sources render the same sprite name, the build reports `<family>.duplicate_sprite_name` against the later source before emission.

Dry-run-only custom registries may omit artifact writers. Once a registry registers any artifact writer, `plan_build(...)` validates that every planned artifact type has matching writer coverage and reports `build.missing_artifact_writer` before artifact emission.

The HOI4 profile also registers a reusable `sprite_gfx` artifact writer. Generic source families, custom Python-backed compilers, and the built-in idea family can plan `SpriteType` payloads to emit `interface/*.gfx` files with deterministic `spriteTypes` declarations. The writer follows the local HOI4 `interface/goals.gfx` and `interface/ideas.gfx` shape checked on 2026-06-07: `spriteTypes = { SpriteType = { name = "..." texturefile = "..." } }`. Built-in idea modules now generate sprite declarations for authored `icon.*` files; other asset families still preserve/copy authored image files until a family-specific sprite policy is added.

Projects can also declare first-pass project-local families in `paradev.yaml`. These declarations extend the selected profile registry for normal SDK and CLI builds, family inspection, and registry-backed discovery. A simple family can compile standalone module PDX and localization:

```yaml
families:
  superevent:
    kind: simple_source
    metadata_keys: [scope]
    source_slots:
      - name: script
        match: script.pdx
        kind: pdx
        required: true
      - name: loc
        match: "**/*.loc"
        kind: loc
        many: true
      - name: icon
        match: "^icon\\.(png|dds)$"
        regex: true
        kind: copy
    sprite_slots: [icon]
    templates:
      pdx: events/superevents/{object_id}.txt
      loc: localisation/{language_folder}/{object_id}_{language}.yml
      copy: gfx/superevents/{object_id}{source_suffix}
      sprite_gfx: interface/paradev_{family}.gfx
      sprite_name: GFX_superevent_{object_id}
    asset_constraints:
      icon:
        formats: [dds]
        width: 64
        height: 64
```

This lets a module such as `modules/superevent/FALL_OF_PARIS/` compile through the same generic `SimpleSourceFamily` path as built-in profile families. Declarative project-local families support `pdx`, `loc`, `copy`, `sprite_gfx`, and `sprite_name` artifact templates plus `sprite_slots`, custom source slots, metadata keys, settings keys, allowed setting values, required settings, required localization keys, and copy-slot asset constraints. Publication migration state is not a `paradev.yaml` compiler option. A standalone Registry extension declares `meta.publication.replaces_families` on its `paradev_build_family` item when a renamed or consolidated family must reconcile older tracked ledger rows. A family-wide targeted artifact build uses those descriptor-owned ids; module and collection targets deliberately ignore them because they do not emit the complete successor family. Replacement ids are not discovery aliases and cannot name an active family, the successor itself, or more than one successor. Collection family `metadata_keys` also allow those top-level keys in collection descriptor metadata. Source-file templates can use `{source_slot}` or `{slot}` in addition to source path fields such as `{source_name}`, `{source_stem}`, and `{source_suffix}`. `Project.load(...)` validates template placeholders up front and reports the manifest path, family id, template key, unknown field, and supported field list before any build work starts. Sprite declarations require a copied texture template, a sprite GFX path template, a sprite name template, and at least one copied slot listed in `sprite_slots`.
Duplicate rendered sprite names are blocking diagnostics, so project-local declarations can use a simple template such as `GFX_superevent_{object_id}` without risking silent overwrites.

A routed family can select artifact templates from one metadata setting:

```yaml
families:
  character:
    kind: routed_source
    route_setting: settings.subtype
    settings_normalizers:
      subtype: lower_snake
    source_slots:
      - name: def
        match: def.txt
        kind: pdx
        required: true
      - name: loc
        match: "**/*.loc"
        kind: loc
        many: true
      - name: portrait
        match: "^portrait\\.(png|dds)$"
        regex: true
        kind: copy
    routes:
      advisor:
        pdx: common/advisors/{object_id}.txt
        loc: localisation/{language_folder}/{object_id}_{language}.yml
        copy: gfx/interface/advisors/{object_id}{source_suffix}
      commander:
        pdx: common/commanders/{object_id}.txt
        loc: localisation/{language_folder}/{object_id}_{language}.yml
        copy: gfx/interface/commanders/{object_id}{source_suffix}
    sprite_slots: [portrait]
    templates:
      sprite_gfx: interface/paradev_{family}.gfx
      sprite_name: GFX_character_{object_id}
```

`routed_source` declarations use the generic `RoutedSourceFamily`. The `route_setting` defaults to `settings.subtype` when omitted, and every route id becomes an allowed and required value in the family inspection payload. `settings_normalizers` currently accepts the named strategy `lower_snake`, so a module such as `modules/character/GER_advisor/meta.yaml` can set `settings.subtype: Advisor` or `settings.subtype: advisor` and use the `advisor` artifact templates without adding Python code. Python-backed `RoutedSourceFamily` registrations can also aggregate selected copied slots into one family-level sprite GFX artifact; each route keeps its own copy template, while the shared sprite template records the routed texture paths.

Routes emit artifacts by default and must define at least one route-level template. A metadata variant that intentionally produces no generic artifacts can instead declare only `emits_artifacts: false`. The family inspection payload keeps that route in the setting values and represents it as `{"emits_artifacts": false}`, while omitting it from output contracts. Non-emitting routes cannot also declare artifact templates.

Declarative routed families support the same sprite aggregation shape: route-level `copy` templates keep texture output route-specific, while top-level `templates.sprite_gfx`, `templates.sprite_name`, and `sprite_slots` define the shared sprite declaration. Top-level `templates.pdx`, `templates.loc`, and `templates.copy` stay invalid for `routed_source`; those output templates belong under each route.

A collection family can compile sibling modules plus optional collection descriptors under `collections/<family>/<collection>/`:

```yaml
families:
  news_event:
    kind: collection_source
    source_slots:
      - name: body
        match: body.txt
        kind: pdx
        required: true
    collection_source_slots:
      - name: header
        match: header.txt
        kind: pdx
      - name: strings
        match: strings.loc
        kind: loc
    templates:
      pdx: events/{collection_id}.txt
      module_pdx: events/{object_id}.txt
      loc: localisation/{language_folder}/{object_id}_{language}.yml
```

`collection_source` declarations use the generic `CollectionSourceFamily`: descriptor PDX is prepended to member module PDX in the collection-owned artifact, descriptor localization and copy slots emit collection-owned artifacts even when no PDX source is authored, and uncollected modules can fall back to `module_pdx` when that template is declared. Descriptor-only collections are valid when the descriptor owns at least one matched source slot. Project-local declarations remain intentionally narrow: `simple_source`, `routed_source`, and `collection_source` use generic family helpers.

For hand-authored project-local families, declare one trusted Python registry module per
entity family in `paradev.yaml`:

```yaml
python_modules:
  - tools/families/notice.py
```

Each module is imported from the project and must expose a callable `register(registry)`. The function can mutate the selected profile registry:

```python
from paradev.build import SimpleSourceFamily, Slot


def register(registry):
    registry.add(
        SimpleSourceFamily(
            family="notice",
            pdx_path_template="common/notices/{object_id}.txt",
            source_slots=(Slot("def", "def.txt", required=True, kind="pdx"),),
        )
    )
```

Python modules run before declarative `families`, so declarative entries can still cover tiny generated or template-only cases while Python stays the normal hand-authored family path. Python-backed artifact templates must be non-empty strings and are validated with the same supported placeholder fields as declarative families before they appear in family inspection or build payloads. Python-backed simple and routed sprite declarations require copied texture output, a sprite GFX template, a sprite name template, and at least one `sprite_slots` entry; routed declarations may satisfy copied texture output through route-level copy templates. Python-backed family `source_slots` and `collection_source_slots`, plus profile-level `BuildRegistry.source_slots` and `BuildRegistry.collection_source_slots` defaults, must be `Slot` lists with non-empty `name` and `match`, boolean flags, and an optional non-empty string `kind`. Python-backed family `metadata_keys`, `settings_keys`, and `required_settings` must be strings or string lists, `settings_values` must map setting keys to strings or string lists, and `settings_normalizers` must map setting keys to callables. Settings normalizer failures are reported as `family.invalid_setting` build diagnostics with module metadata context instead of aborting the SDK build call. Family `normalize(...)`, `check(...)`, and `emit(...)` failures are reported as `family.normalize_failed`, `family.check_failed`, or `family.emit_failed` diagnostics, include the failing `family`, and block that family's artifact emission for the current build. Invalid `normalize(...)` return values, dropped module ids, and family changes are also reported as `family.normalize_failed`; missing `emit(...)`, invalid `check(...)` diagnostic values, and invalid `emit(...)` artifact values are reported through their matching hook diagnostics instead of aborting the SDK build call. Python-backed `required_loc_keys` may use only `{family}`, `{module_id}`, `{collection_id}`, and `{object_id}` template fields. Python-backed `asset_constraints` must map non-empty slot names to at least one `formats`, `width`, or `height` rule; formats are strings or string lists, and dimensions are positive integers. Generic routed families registered from Python must declare a non-empty unprefixed `settings_key`, at least one route, non-empty string route ids, and at least one artifact template per route, matching the manifest validation contract before broken route tables appear in family inspection or build payloads. SDK callers that pass an explicit `registry=` bypass manifest registry extensions and use that registry unchanged.

A family that must prepare the same expensive state for both validation and
emission may expose `compile(...) -> FamilyCompileResult`. The planner calls it
once and reports contract or runtime failures as `family.compile_failed`.
Ordinary families keep the simpler `check(...)` plus `emit(...)` protocol.

## Inspect PDX Parse

To inspect one authored PDX file without running a project build:

```bash
rtk uv run paradev parse demos/assets/projects/minimal/src/modules/focus/GER_sample/def.txt --json
```

SDK callers can use the same payload contract:

```python
from paradev.sdk import parse_pdx_file

payload = parse_pdx_file("demos/assets/projects/minimal/src/modules/focus/GER_sample/def.txt", include_tokens=True)
```

This prints a `paradev.pdx.parse.v1` payload with the resolved path, file extension, `ok` flag, lossy JSON `data` projection when parsing succeeds, and structured parser diagnostics when parsing fails. The CLI delegates to `parse_pdx_file(...)` so Python SDK, script, GUI, MCP, and CLI callers share one parse payload. The generic build PDX loader uses the same SDK parser with `include_dump=True`, then maps SDK diagnostics into build `Diagnostic` rows with module, collection, slot, and relative source-path context. Add `--dump` or `include_dump=True` to include the lossless PDX dump that preserves comments, duplicate entries, operators, scalar annotations, and file-extension metadata for round-trip tooling. Add `--tokens` or `include_tokens=True` when parser, editor, or importer integrations need lexer token rows with source line and column spans. Invalid PDX or unreadable source paths exit non-zero in the CLI after printing the diagnostic payload, while the SDK returns `ok: false`, so scripts can fail fast while still showing line and column context when the parser has it.

Dynamic and scripted references stay intact as scalar values in parse output, including token-start dotted references such as `@FROM.FROM`, embedded references such as `distance_to@ROOT.capital`, bracketed scripted values such as `[GetHitlerHandshakeEventPicture]`, fallback defaults such as `global.days_add_support?1337`, array selectors such as `global.monroe_countries_in_support^num` and `SOV_military_offensive_states^0`, and unquoted asset paths such as `gfx/interface/technologies/ger_basic_light_td.dds`.

## Minimal Demo

The demo project lives at:

```bash
demos/assets/projects/minimal
```

Its first module is:

```text
src/modules/focus/GER_sample/
  meta.yaml
  def.txt
  main.loc
```

Run a dry build plan:

```bash
rtk uv run paradev build demos/assets/projects/minimal --json
```

The dry run discovers `focus/GER_sample`, derives `GER_main`, and plans:

- `common/national_focus/GER_main.txt` under `output`
- `views/focus-tree/GER_main.json` under `build`
- `localisation/english/GER_sample_l_english.yml` under `output`

The module metadata also declares dependency edges:

- `requires`: `idea:GER_industrial_spirit`
- `after`: `focus:GER_rhineland`

Localization `.loc` files may use full HOI4 language ids such as `l_english` or common aliases such as `en`, `fr`, `de`, `ru`, and `zh`; the loader normalizes those aliases before planning `localisation/<language>/...` YML artifacts. Missing matched localization sources report `loc.missing_source`; matched files that cannot be read report `loc.unreadable_source`. Duplicate canonical localization keys for the same language are blocking diagnostics within one module and across discovered project modules, so `en.GER_sample` and `l_english.GER_sample` cannot silently emit ambiguous YML.

Resolvable `after` edges between discovered modules are used for deterministic family emission order. Explicit project-local targets such as `module:focus/GER_x` or `focus/GER_x` must resolve to discovered modules. Invalid dependency metadata, missing project-local targets, and `after` cycles produce blocking diagnostics anchored to `meta.yaml`. Reference-style game symbols such as `focus:GER_rhineland` and `idea:GER_industrial_spirit` stay in the dependency graph until game reference indexes are available.

When module metadata provides `collection`, builds derive collection records automatically. Optional descriptors under `collections/<family>/<collection>/meta.yaml` or `collection.yaml` attach collection-level metadata. Explicit SDK `collections=` remain authoritative for tests and custom callers.

If a focus module has no collection metadata yet, the HOI4 profile falls back to the older module-owned PDX output path so a single module can still build.

The focus collection compiler currently blocks duplicate focus IDs and missing project-local PDX prerequisites. Those diagnostics include PDX line and column spans for the duplicate ID or missing prerequisite value when parser source positions are available. Reference-backed prerequisite validation remains a later game-index slice.

When a focus module provides localization entries, each localized language must include `<focus_id>` and `<focus_id>_desc`. Missing keys produce blocking diagnostics anchored to the focus id source span. Modules without localization source remain allowed in the current scaffold so parser and PDX-only workflows keep working.

Missing matched PDX sources report `pdx.missing_source`; matched files that cannot be read report `pdx.unreadable_source`. Malformed PDX sources in matched source slots produce blocking parser diagnostics before artifact planning continues for that source. The build graph receives those diagnostics from the same SDK parse payload used by `paradev parse`, so CLI, SDK, desktop, REST, and future MCP clients share parser codes and source spans. For example, an operator with no following value reports `pdx.missing_value` at the operator's line and column, an unterminated quoted string reports `pdx.unterminated_string` at the opening quote, an unterminated bracketed value reports `pdx.unterminated_bracket_value` at `[`, a bare variable marker reports `pdx.empty_variable` at `@`, and an empty hex literal reports `pdx.invalid_hex_number` at the literal start, so callers can point users to the exact syntax fix.

The default HOI4 scaffold emits a `focus-tree.view.v1` planning artifact for focus collections. That artifact records deterministic focus node order, module ids, source paths, source spans, and project-local prerequisites for future GUI and layout passes. Artifact JSON includes `target_root`: `output` for game-ready mod files and `build` for ParaDev-owned files under `.paradev/.cache/build`.

Static copy slots preserve their matched relative source path under `gfx/paradev/{object_id}/`, so nested files such as `assets/interface/icon.png` and `copy/interface/icon.png` remain distinct generated artifacts. Missing matched copy sources report `copy.missing_source`; matched files that cannot be read report `copy.unreadable_source`. Copy artifact metadata always includes slot, relative source path, output path, byte size, HeavenBase's deterministic source hash, and a separate `content_sha256` over the exact file bytes. PNG, DDS, and TGA sources also include media type, lowercase format, width, and height when their headers are readable. Families that declare asset constraints validate against that header-derived metadata before planning copy artifacts. During artifact emission, the static-copy writer validates the planned source. If an existing output has the exact `content_sha256`, publication can retain it without rereading or staging the source; a missing or mismatched output takes the normal exact render/copy path, which repairs external target changes and rejects source drift. Invalid hashes, oversized direct-copy inputs, and artifacts affected by a registered stage transform fall back or fail closed rather than bypassing validation.

Dry run is the default and does not write game output files.

## Emit Artifacts

To write game-ready files under the project's `output_root`:

```bash
rtk uv run paradev build demos/assets/projects/minimal --emit-artifacts --json
```

If the build has blocking diagnostics, the CLI prints the structured dry-run build payload with those diagnostics, exits non-zero, and does not write artifacts. Run the same command after fixing the reported source issue.

For the demo project, this writes under `demos/assets/projects/minimal/build/mod/`:

```text
common/national_focus/GER_main.txt
localisation/english/GER_sample_l_english.yml
```

The focus-tree view writes under the project's `build_root` instead of the mod `output_root`:

```text
views/focus-tree/GER_main.json
```

Custom SDK callers that use `write_artifacts(...)` directly should pass an unblocked build result and artifacts for one `target_root` at a time. `Project.build(..., emit_artifacts=True)` handles the blocked-build check and target-root split automatically. Artifact paths must be relative and stay under their selected target root; paths with parent traversal such as `../` report `build.invalid_artifact_path` during planning and are rejected again by artifact writers before any file is written. Static copy artifacts may also be rejected at emission time if the source file changed, became unreadable, or cannot be copied into the target tree.

Generated output should not be committed unless a future fixture explicitly needs it.

## Inspect Modules

To inspect discovered modules without reading the full build plan:

```bash
rtk uv run paradev modules demos/assets/projects/minimal --json
```

Use `--family`, `--module`, `--collection`, and `--slot` to narrow the rows:

```bash
rtk uv run paradev modules demos/assets/projects/minimal --family focus --module focus/GER_sample --collection GER_main --slot def --json
```

SDK callers can use the same payload through:

```python
from paradev.sdk import Project

payload = Project.load("demos/assets/projects/minimal").modules(family="focus", source_slot="def")
```

This runs a fresh dry build plan and returns the `paradev.build.modules.v1` payload with module id, family, source root, source slots, metadata, optional collection id, and a deterministic `index` keyed by module id, family, collection, and source slot. It does not write generated files.

## Inspect Collections

To inspect discovered collections without reading the full build plan:

```bash
rtk uv run paradev collections demos/assets/projects/minimal --json
```

Use `--family`, `--collection`, and `--module` to narrow the rows. Use
`--slot` when you only want collections whose descriptor authored a matching
source slot:

```bash
rtk uv run paradev collections demos/assets/projects/minimal --family focus --collection GER_main --module focus/GER_sample --json
```

SDK callers can use the same payload through:

```python
from paradev.sdk import Project

payload = Project.load("demos/assets/projects/minimal").collections(family="focus", collection_id="GER_main")
```

SDK callers can pass `source_slot="loc"` or another descriptor slot name for
the same slot filtering. This runs a fresh dry build plan and returns the
`paradev.build.collections.v1` payload with collection id, family, member module
ids, descriptor source slots when authored, metadata, and a deterministic
`index` keyed by collection id, family, member module id, and descriptor source
slot. It does not write generated files.

## Inspect Artifacts

To inspect planned artifacts without reading the full build payload:

```bash
rtk uv run paradev artifacts demos/assets/projects/minimal --json
```

Use `--type`, `--target-root`, `--owner`, `--path`, `--mode`, `--module`, and `--collection` to narrow the rows. `--owner` is an exact artifact-owner filter such as `collection:GER_main`; `--module` and `--collection` match artifacts owned by that source unit or artifacts that record that module or collection in their metadata, such as collection-owned focus output and focus-tree view artifacts.

```bash
rtk uv run paradev artifacts demos/assets/projects/minimal --type pdx --target-root output --collection GER_main --path common/national_focus/GER_main.txt --json
```

SDK callers can use the same payload through:

```python
from paradev.sdk import Project

payload = Project.load("demos/assets/projects/minimal").artifacts(
    artifact_type="pdx",
    target_root="output",
    collection_id="GER_main",
)
```

This runs a fresh dry build plan and returns the `paradev.build.artifacts.v1` payload with artifact path, type, owner, source inputs, mode, target root, metadata, and a deterministic `index` keyed by artifact path, type, owner, target root, mode, contributing module, and related collection. Artifact paths that are absolute or contain parent traversal report `build.invalid_artifact_path`. It does not write generated files.

## Inspect Localization

To inspect loaded localization rows without reading build manifest files directly:

```bash
rtk uv run paradev localization demos/assets/projects/minimal --json
```

Use `--language`, `--key`, `--key-prefix`, `--module`, and `--collection` to narrow the rows:

```bash
rtk uv run paradev localization demos/assets/projects/minimal --language en --key GER_sample_desc --module focus/GER_sample --json
```

SDK callers can use the same payload through:

```python
from paradev.sdk import Project

payload = Project.load("demos/assets/projects/minimal").localization(language="en", key="GER_sample_desc")
```

This runs a fresh dry build plan and returns the `paradev.build.localization.v1` payload with canonical language, key, text, module id or collection id, source path, resolved source metadata, duplicate state, and a language/key index. The index maps each language and key to row numbers in the returned payload, so filtered SDK and CLI responses can still support exact lookup without reading manifest files directly. It does not write generated files.

## Inspect Assets

To inspect planned static copy assets without reading build manifest files directly:

```bash
rtk uv run paradev assets demos/assets/projects/minimal --json
```

Use `--family`, `--module`, `--collection`, `--slot`, and `--format` to narrow the rows:

```bash
rtk uv run paradev assets demos/assets/projects/minimal --family focus --module focus/GER_sample --slot assets --format png --json
```

SDK callers can use the same payload through:

```python
from paradev.sdk import Project

payload = Project.load("demos/assets/projects/minimal").assets(module_id="focus/GER_sample", slot="assets")
```

This runs a fresh dry build plan and returns the `paradev.build.assets.v1` payload with module id or collection id, family, slot, source path, artifact path, artifact owner, target root, hash/size metadata, image metadata when available, resolved source metadata, and an owner/slot index. It does not write generated files.

## Inspect Sprites

To inspect planned interface sprite declarations without parsing generated `.gfx` files:

```bash
rtk uv run paradev sprites demos/assets/projects/minimal --json
```

Use `--family`, `--module`, `--collection`, `--slot`, and `--name` to narrow the rows:

```bash
rtk uv run paradev sprites demos/assets/projects/minimal --family idea --slot icon --name GFX_idea_GER_industry_spirit --json
```

SDK callers can use the same payload through:

```python
from paradev.sdk import Project

payload = Project.load("demos/assets/projects/minimal").sprites(family="idea", slot="icon")
```

This runs a fresh dry build plan and returns the `paradev.build.sprites.v1` payload with sprite name, texture file, owning sprite GFX artifact, target root, module id or collection id when known, source family, source slot, resolved source metadata, and an owner/slot index. It does not write generated files.

## Inspect Diagnostics

To inspect build diagnostics without reading build manifest files directly:

```bash
rtk uv run paradev diagnostics demos/assets/projects/minimal --json
```

Use `--severity`, `--code`, `--family`, `--owner`, `--target-root`, `--module`, `--collection`, `--source`, and `--slot` to narrow the rows:

```bash
rtk uv run paradev diagnostics demos/assets/projects/minimal --severity error --code focus.missing_localization --family focus --module focus/GER_sample --source def.txt --slot loc --json
```

SDK callers can use the same payload through:

```python
from paradev.sdk import Project

payload = Project.load("demos/assets/projects/minimal").diagnostics(
    severity="error",
    family="focus",
    source_path="def.txt",
    slot="loc",
)
```

This runs a fresh dry build plan and returns the `paradev.build.diagnostics.v1` payload with diagnostic code, severity, message, family, module id or collection id, source path, slot, source span when available, resolved source metadata, a severity/code `index`, and a `family_index` keyed by family, severity, code, and returned row number. Family, owner, target-root, source, and slot filters apply to the diagnostic row fields and the resolved `source` object, so callers can use either the diagnostic's logical anchor or the authored source file path and slot shown in the payload. Diagnostics that involve multiple source slots, such as slot-collision errors, include a `slots` list and match `--slot` against any listed slot. Duplicate artifact path diagnostics include `target_root` and an `owners` list, and match `--owner` against either producer. Missing artifact-writer diagnostics include the planned artifact `target_root` and are emitted once per missing artifact type and target root. Invalid artifact target-root diagnostics include the rejected `target_root` value so CLI, SDK, GUI, and future MCP clients can filter by the exact bad root. Untracked artifact-input warnings include the artifact `target_root` so build-root planning artifacts do not look like output-root files. It does not write generated files.

## Inspect Sources

To inspect the compiler input inventory without reading build manifest files directly:

```bash
rtk uv run paradev sources demos/assets/projects/minimal --json
```

Use `--module`, `--collection`, `--family`, `--slot`, `--loader`, and `--status` to narrow the rows:

```bash
rtk uv run paradev sources demos/assets/projects/minimal --module focus/GER_sample --slot def --loader pdx --status loaded --json
```

SDK callers can use the same payload through:

```python
from paradev.sdk import Project

payload = Project.load("demos/assets/projects/minimal").sources(module_id="focus/GER_sample", loader="pdx")
```

This runs a fresh dry build plan and returns the `paradev.build.sources.v1` payload with module-owned and collection-owned source rows, resolved source path, relative path, slot, generic loader (`pdx`, `loc`, `copy`, or `unknown`), load status (`loaded`, `matched`, or `diagnostic`), loader-specific summaries such as PDX entry count, localization languages, or static-copy metadata, and an owner/slot index. It does not write generated files. Use this payload when a GUI, importer, MCP tool, or script needs to show what ParaDev recognized before explaining which artifacts those sources emit.

## Inspect Source Map

To inspect artifact-to-source traceability without reading build manifest files directly:

```bash
rtk uv run paradev source-map demos/assets/projects/minimal --json
```

Use `--module`, `--collection`, `--family`, `--slot`, `--type`, and `--target-root` to narrow the rows:

```bash
rtk uv run paradev source-map demos/assets/projects/minimal --module focus/GER_sample --slot def --type pdx --target-root output --json
```

SDK callers can use the same payload through:

```python
from paradev.sdk import Project

payload = Project.load("demos/assets/projects/minimal").source_map(module_id="focus/GER_sample", slot="def")
```

This runs a fresh dry build plan and returns the `paradev.build.source-map.v1` payload with artifact path, artifact type, target root, artifact owner, raw inputs, resolved source metadata, and an owner/slot index. It does not write generated files.

## Inspect Dependencies

To inspect build dependency edges without reading build manifest files directly:

```bash
rtk uv run paradev dependencies demos/assets/projects/minimal --json
```

Use `--module`, `--source`, `--target`, and `--kind` to narrow the rows. `--module` accepts either `focus/GER_sample` or the manifest source value `module:focus/GER_sample`; `--source` also treats bare module ids as `module:<id>` for module-owned edges:

```bash
rtk uv run paradev dependencies demos/assets/projects/minimal --module focus/GER_sample --kind requires --target idea:GER_industrial_spirit --json
```

SDK callers can use the same payload through:

```python
from paradev.sdk import Project

payload = Project.load("demos/assets/projects/minimal").dependencies(module_id="focus/GER_sample", kind="requires")
```

This runs a fresh dry build plan and returns the `paradev.build.dependencies.v1` payload with source, target, kind, optional metadata, and a source/kind index. It does not write generated files.

## Inspect Build Graph

To inspect source-to-artifact and dependency relationships as one graph:

```bash
rtk uv run paradev build-graph demos/assets/projects/minimal --json
```

Use the same source and artifact filters as `source-map`, plus `--kind` for edge kinds such as `emits`, `requires`, or `after`:

```bash
rtk uv run paradev build-graph demos/assets/projects/minimal --module focus/GER_sample --kind requires --json
```

SDK callers can use the same payload through:

```python
from paradev.sdk import Project

payload = Project.load("demos/assets/projects/minimal").build_graph(module_id="focus/GER_sample")
```

This runs a fresh dry build plan and returns the `paradev.build.graph.v1` payload with deterministic graph nodes, graph edges, node/edge counts, and type/kind indexes. The graph composes the source-map and dependency manifests so users can see which authored files emit which artifacts and which module dependencies still point to external reference symbols. Artifact nodes include `module_ids` and `collection_ids` when provenance is known, so collection-owned outputs remain navigable from the contributing modules. It does not write generated files.

## Inspect Build Explanation

To inspect one module without combining separate manifest payloads by hand:

```bash
rtk uv run paradev build-explain demos/assets/projects/minimal --module focus/GER_sample --json
```

To inspect one collection and see collection-owned artifacts plus contributing
descriptor and member-module sources:

```bash
rtk uv run paradev build-explain demos/assets/projects/minimal --collection GER_main --json
```

To inspect one planned artifact and see the source slots that emitted it:

```bash
rtk uv run paradev build-explain demos/assets/projects/minimal --artifact common/national_focus/GER_main.txt --target-root output --json
```

To inspect one authored source file and see which artifacts it contributes to:

```bash
rtk uv run paradev build-explain demos/assets/projects/minimal --source src/modules/focus/GER_sample/def.txt --json
```

To inspect diagnostics that may not have a source or artifact anchor, such as project-local Python family hook failures:

```bash
rtk uv run paradev build-explain demos/assets/projects/minimal --diagnostic-code family.normalize_failed --json
```

SDK callers can use the same payload through:

```python
from paradev.sdk import Project

payload = Project.load("demos/assets/projects/minimal").build_explain(module_id="focus/GER_sample")
collection_payload = Project.load("demos/assets/projects/minimal").build_explain(collection_id="GER_main")
source_payload = Project.load("demos/assets/projects/minimal").build_explain(
    source_path="src/modules/focus/GER_sample/def.txt",
)
artifact_payload = Project.load("demos/assets/projects/minimal").build_explain(
    artifact_path="common/national_focus/GER_main.txt",
    target_root="output",
)
diagnostic_payload = Project.load("demos/assets/projects/minimal").build_explain(
    diagnostic_code="family.normalize_failed",
)
```

This runs a fresh dry build plan and returns the `paradev.build.explain.v1` payload. Module targets include the selected module, summary counts, source files, planned artifacts, outgoing module dependency edges, related diagnostics, and the related `build-graph` subset. Collection targets include the selected collection, member module ids, descriptor source slots when authored, collection-owned artifacts, contributing descriptor and member-module sources, member dependency edges, related diagnostics, and the related graph subset. Source targets include the selected source file, artifacts it emits, source-linked diagnostics, and the emits-only graph subset. Artifact targets include the selected artifact, source files that emitted it, source-linked diagnostics, and the emits-only graph subset. Artifact graph nodes retain module and collection provenance in `module_ids` and `collection_ids`. Diagnostic-code targets include every matching diagnostic row, plus any resolved source or artifact context when the diagnostic has one; artifact diagnostics that include `target_root` resolve artifact context by both path and target root, so output-root collisions do not pull in same-path build-root planning artifacts. Collision diagnostics also include the exact artifact graph node even when the colliding artifacts have no source-slot inputs; duplicate output-location nodes aggregate `owners`, `module_ids`, and `collection_ids` so GUI, MCP, and script surfaces can show who is competing for that generated path. Unanchored hook and hook-contract failures still return a blocking explanation with the failing `family` and an empty graph. It is meant for GUI, MCP, and script surfaces that need to answer "what happened to this module?", "what did this collection compile?", "what did this source file produce?", "what produced this artifact?", or "why did this diagnostic block the build?" without teaching users the lower-level manifest model. It does not write generated files or `.paradev/.cache/build` manifests.

Exactly one of `--module`, `--collection`, `--source`, `--artifact`, or `--diagnostic-code` must be passed, and target values must be non-empty. `--target-root` is only valid with `--artifact`. Unknown targets are reported against the requested target value; for project-relative source paths, the error keeps the relative path rather than leaking the resolved absolute path.

## Inspect HeavenBase Catalog Preview

To inspect the read-only HeavenBase-ready catalog rows without creating a workspace database:

```bash
rtk uv run paradev hb catalog-preview demos/assets/projects/minimal --json
```

SDK adapter callers can use the same read-only payload through:

```python
payload = Project.load("demos/assets/projects/minimal").inspect("catalog-preview")
```

This runs a fresh dry build plan and returns the `paradev.hb.catalog-preview.v1` payload with deterministic row groups for `project`, `source-file`, `build-artifact`, `build-dependency`, `build-graph-node`, `build-graph-edge`, `loc-entry`, `asset`, `sprite`, `pdx-document`, `pdx-symbol`, `hoi4-entity`, and `diagnostic`, plus counts for each group. `source-file` rows are derived from `sources.json`, so catalog users see the same owner, root, relative path, slot, loader, status, loader-specific summaries, and diagnostic codes as `Project.sources(...)`. Build artifact rows include top-level `module_ids` and `collection_ids` when provenance is known, so catalog users can find collection-owned artifacts that a module contributed to without decoding nested artifact metadata. PDX document rows include the source file, entry count, and AST hash. PDX symbol rows include the key path, source span, scalar value where applicable, and owning module or collection. Build graph rows mirror the `build-graph` payload so persisted catalog inspection can find source-to-artifact and dependency relationships. It is a preview bridge from SDK manifests to the future HeavenBase workspace layer and does not write `.paradev/hb` files.

To validate those rows against a real in-memory HeavenBase workspace:

```bash
rtk uv run paradev hb catalog-smoke demos/assets/projects/minimal --json
```

This returns the `paradev.hb.catalog-smoke.v1` payload with the registered `paradev-*` schema entities, preview row counts, upserted row counts, Catalog row counts, and MetaSchema entity count. It is still read-only for the project: no `.paradev/hb` files are created.

To create a local SQLite HeavenBase catalog database from the same preview:

```bash
rtk uv run paradev hb catalog-write demos/assets/projects/minimal --json
```

This returns the `paradev.hb.catalog-write.v1` payload and writes `.paradev/hb/catalog.sqlite` by default. The command refuses to overwrite an existing `catalog.sqlite`, `catalog.sqlite-wal`, or `catalog.sqlite-shm` file. Use `--database <path>` to write to a different new SQLite file.

To explicitly replace an existing local SQLite catalog:

```bash
rtk uv run paradev hb catalog-refresh demos/assets/projects/minimal --json
```

This returns the `paradev.hb.catalog-refresh.v1` payload. Refresh builds the replacement catalog at a sibling staging path first, checkpoints it, then replaces `.paradev/hb/catalog.sqlite` and reports the old database triplet paths it replaced. Use this for repeated local catalog rebuilds; keep `catalog-write` for first writes that should fail if a catalog already exists.

To inspect rows from the written SQLite catalog:

```bash
rtk uv run paradev hb catalog-query demos/assets/projects/minimal --entity pdx-symbol --json
```

SDK adapter callers can use the same read-only query through:

```python
payload = Project.load("demos/assets/projects/minimal").inspect("catalog-query", entity="pdx-symbol")
```

Graph relationships, build artifacts, and compiler inputs can be queried the same way:

```bash
rtk uv run paradev hb catalog-query demos/assets/projects/minimal --entity build-graph-edge --tag requires --json
rtk uv run paradev hb catalog-query demos/assets/projects/minimal --entity build-artifact --tag focus/GER_sample --json
rtk uv run paradev hb catalog-query demos/assets/projects/minimal --entity source-file --tag loader:pdx --json
```

This returns the `paradev.hb.catalog-query.v1` payload by reading `.paradev/hb/catalog.sqlite` in read-only mode. Use `--entity`, `--name`, `--tag`, and `--limit` to narrow the Catalog rows without requiring direct SQLite or HeavenBase workspace knowledge. Each row includes Catalog fields plus `data`, the original preview row stored on the target entity. Build artifact catalog tags include contributing module ids and related collection ids when the preview can derive them from artifact metadata. Source catalog tags include simple module/family/slot tags plus prefixed tags such as `module:<id>`, `collection:<id>`, `family:<family>`, `slot:<slot>`, `loader:<loader>`, and `status:<status>`.

## Emit Manifests

To write build manifests under the project's `build_root`:

```bash
rtk uv run paradev build demos/assets/projects/minimal --emit-manifests --json
```

This writes `.paradev/.cache/build/*.json`, including `modules.json`, `collections.json`, `artifacts.json`, `dependencies.json`, `diagnostics.json`, `assets.json`, `sprites.json`, `localization.json`, `sources.json`, and `source-map.json`. Each manifest records the build `profile` when the build was run through `Project.build(...)` or `plan_build(..., profile=...)`, so saved artifacts can be traced back to the selected compiler profile. The modules manifest records discovered modules with their family, source root, source slots, metadata, optional collection id, and a deterministic id/family/collection/slot `index`. The collections manifest records discovered collections with their family, member module ids, descriptor source slots when authored, metadata, and a deterministic id/family/module/slot `index`. The artifacts manifest records planned output and build-root artifacts with path, type, owner, inputs, mode, target root, metadata, and a deterministic path/type/owner/target-root/mode/module/collection `index` so owned artifacts and collection-owned artifacts with module provenance are both discoverable. HOI4 descriptor rows use artifact type `mod_descriptor`; the output-root row is `descriptor.mod`, and the build-root row is `launcher/<project_id>.mod`. The dependency manifest records `requires` and `after` edges from module metadata plus a deterministic source/kind `index`. The asset manifest records each planned static copy asset with module id or collection id, family, slot, source path, generated artifact path, artifact owner, target root, hash/size metadata, image metadata when available, resolved source metadata, and a deterministic owner/slot `index` for editor and MCP surfaces. The sprite manifest records each planned interface sprite declaration with sprite name, texture file, owning sprite GFX artifact, target root, source metadata, and a deterministic owner/slot `index`. The localization manifest records each loaded localization row with canonical language, key, text, module id or collection id, source path, resolved source metadata, a project-wide duplicate flag, and a deterministic `index` keyed by language and localization key for editor and MCP surfaces. The sources manifest records module-owned and collection-owned compiler inputs with source root, relative path, slot, loader, load status, loader-specific summaries, diagnostic codes when applicable, and a deterministic owner/slot `index`. The source map records artifact path, artifact type, owner, raw source inputs, traceable `sources` entries with module id or collection id, family, and slot where available, and a deterministic owner/slot `index`. Artifact inputs that cannot be matched to a discovered source slot produce non-blocking `build.untracked_artifact_input` warnings with the owning artifact target root. Diagnostics keep their original module id or collection id, source path, and span fields; `diagnostics.json` also adds a resolved `source` object with module id or collection id, family, slot, and normalized path when that source is known plus a deterministic severity/code `index` and additive `family_index`. This lets SDK, CLI, desktop, and future MCP surfaces trace outputs, assets, sprites, dependencies, and validation errors back to authored files without guessing from paths.

Generated manifests should not be committed unless a future fixture explicitly needs them.

## Profile Override

The build profile defaults to the project `game` field. To override it:

```bash
rtk uv run paradev build demos/assets/projects/minimal --profile hoi4 --json
```

Unknown profiles are rejected by the SDK profile registry.

Build JSON and manifest JSON include the resolved `profile` field. By default this is the project `game` value, such as `hoi4`.
