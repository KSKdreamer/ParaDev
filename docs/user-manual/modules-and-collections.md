# Modules And Collections

## English

The user-facing model is small:

1. A project contains modules.
2. Some modules are grouped into collections.
3. A build profile turns modules and collections into artifacts.

A module is a folder:

```text
src/modules/idea/GER_industry_spirit - German Industry Spirit/
  def.txt
  main.loc
  icon.dds
```

The logical module id is `family/object_id`. Its physical folder defaults to
`object_id`, but current user-facing templates should use
`object_id - preferred-language title`. The folder prefix remains the stable
game/module identity; the suffix is the human-readable title. ParaDev keeps
the authored localization unchanged while making only that folder suffix
portable: it removes Clausewitz color, icon, live-value, and `$...$`
substitutions, collapses line breaks, replaces filesystem-reserved
punctuation, removes trailing dots, and truncates safely at the 255-byte
component boundary. A title such as `Progress ([?ROOT.progress|Y0]/4)` is
therefore stored verbatim in `main.loc` while the folder stays simply
`ID - Progress`.

The registered family owns the ordered localization keys used for its display
title through hidden `title_loc_keys`. For example, PIHC3 countries prefer
`{object_id}_DEF`, intelligence agencies prefer `{object_id}_NAME`, and
operative codenames prefer `{object_id}_NAME_THEME`. An explicit empty list
disables dynamic localization titles and uses the readable folder suffix.
The SDK browser and desktop consume this Registry contract; clients do not
guess family-specific title keys.

Rename a module when you want to move that source container:

```bash
rtk uv run paradev module-rename projects/starter-mod modifier/starter_mod_starter_modifier starter_mod_renamed_modifier --json
```

This changes the ParaDev module id and folder path only. If the folder has a
readable suffix such as `TECHNOLOGY_FIREARM_I - Basic Firearms`, rename
preserves that suffix. It does not rewrite HoI4 ids inside `def.txt`,
localization keys, or other authored files.

To synchronize the readable suffix after editing the Registry-owned
localization title, pass the title explicitly. The logical id may remain
unchanged:

```bash
rtk uv run paradev module-rename projects/starter-mod \
  technology/TECHNOLOGY_FIREARM_I TECHNOLOGY_FIREARM_I \
  --title "Improved Firearms" --json
```

The desktop **Name** field submits the resolved `title_loc_keys` localization
edit and the canonical readable folder move through one guarded SDK draft
transaction. A failed folder move rolls the completed localization write
back, so the renderer never has to coordinate two independent source calls.
It does not create `meta.yaml` just to persist a display title.

Modules and collections share one Registry-owned localization table in the
desktop. Selecting a Decision category, Focus tree, or other collection shows
the same languages, keys, coverage, and guarded edits as selecting a module;
authors do not open or merge raw `.loc` files just because the text belongs to
a collection. The SDK uses one discriminated target instead of parallel APIs:

```python
workspace = project.localization_workspace(
    "DECISION_CATEGORY_TEST",
    target_kind="collection",
    family="decision",
)
plan = project.plan_localization_update(
    "DECISION_CATEGORY_TEST",
    {
        "op": "set",
        "language": "en",
        "key": "DECISION_CATEGORY_TEST",
        "value": "Test decisions",
    },
    target_kind="collection",
    family="decision",
)
project.apply_source_draft(source_edits=plan["source_edits"])
```

Workspace and plan payloads identify their source unit with
`target.kind`, `target.id`, `target.family`, and `target.object_id`. Every
source reports a `unit_relative_path`. REST and MCP accept the equivalent
`target_kind`, `target_id`, and optional `family`; all planners remain
read-only until their returned edits are explicitly applied.

Plan a module removal before deleting the source folder:

```bash
rtk uv run paradev module-remove projects/starter-mod modifier/starter_mod_starter_modifier --json
rtk uv run paradev module-remove projects/starter-mod modifier/starter_mod_starter_modifier --write --json
```

The first command returns `paradev.module.remove.v1` with the file inventory and leaves the folder in place. The second command deletes the module source folder only; generated build artifacts are not touched.

Read or replace one text source file when a GUI, importer, or script needs editor-style access:

```bash
rtk uv run paradev module-file projects/starter-mod modifier/starter_mod_starter_modifier def.txt --json
rtk uv run paradev module-edit projects/starter-mod modifier/starter_mod_starter_modifier def.txt \
  --text "starter_mod_starter_modifier = { stability_factor = 0.10 }" \
  --json
```

`module-edit` preserves the exact text passed to it. Use `--create` only when adding a new file inside an existing module folder.

Use `module-batch-edit` when an importer or migration script generates several module text updates at once. The request JSON has an `edits` array and may set top-level `create` and `encoding` defaults; each edit uses `module_id`, `relative_path`, and `text`, plus optional `source_root`, `create`, and `encoding` overrides. Generate canonical requests with `Project.module_batch_edit_request(...)` from Python or `paradev module-batch-request` from the CLI, then pass the request to `module-batch-edit`; request generation validates that every target module already exists and missing files explicitly opt in to creation. Canonical requests include a `summary` with module count, existing/missing target counts, changed/unchanged target counts, create-enabled rows, and distinct encoding count so generators can report preflight impact before applying. They also include a `targets` array plus `target_index` with one row per edit, including the project-relative target path, existing/created/changed flags, create mode, encoding, and encoded byte size; importers and GUI previews can inspect this without applying the request. Add `--dry-run` to validate and preview the resolved file targets before writing. JSON responses include `created_count`, `updated_count`, and per-file `created` flags so callers can distinguish new migration artifacts from existing module updates. They also include `changed_count`, `unchanged_count`, and per-file `changed` flags so rerunnable migration scripts can report no-op targets without rescanning files; plain CLI output reports both changed/unchanged and updated/created counts in its summary line. In write mode, unchanged targets are validated and included in the response, but their files are not rewritten.

```python
from paradev.sdk import Project

project = Project.load("projects/PIHC3")
request = project.module_batch_edit_request(
    [
        {
            "module_id": "technology/TECHNOLOGY_AIR_CLOUDSHIP",
            "relative_path": "migration/notes.txt",
            "text": "generated\n",
        }
    ],
    create=True,
)
project.write_module_files(request["edits"], create=request["create"], encoding=request["encoding"], write=False)
```

```bash
rtk uv run paradev module-batch-request projects/PIHC3 --create --edit-json '{"module_id":"technology/TECHNOLOGY_AIR_CLOUDSHIP","relative_path":"migration/notes.txt","text":"generated\n"}' > batch-edits.json
rtk uv run paradev module-batch-edit projects/PIHC3 --request batch-edits.json --dry-run --json
rtk uv run paradev module-batch-edit projects/PIHC3 --request batch-edits.json --json
rtk uv run paradev module-batch-edit projects/PIHC3 --request-json '{"edits":[{"module_id":"technology/TECHNOLOGY_AIR_CLOUDSHIP","relative_path":"migration/notes.txt","text":"generated\n","create":true}]}' --json
rtk uv run python scripts/generate_batch_edits.py | rtk uv run paradev module-batch-edit projects/PIHC3 --request - --json
```

Most modules need no visible `meta.yaml`. Use it only for vital choices that
are not already carried by the family folder, object-id prefix, title suffix,
localization, or source files. For example:

```yaml
inactive: true
# comment: Explain why this module is intentionally disabled.
```

ParaDev infers the family from `src/modules/<family>/`, the module ID from the
folder prefix, and the display title from the readable suffix. Do not repeat
the family as `type` or the suffix as `title`. Set `inactive: true` to omit one
module from every build; do not create a second `inactive_modules/` tree.
SDK-owned defaults and graph/import state live under the module-local hidden
`.paradev/` directory and are updated by the SDK transaction that created or
edited them. Module duplication carries forward the durable
`.paradev/meta.yaml` settings needed by the Registry family, while leaving
behind transient import provenance, evidence, diagram state, and transaction
data.
Collection membership is also SDK-owned hidden state. In the desktop editor,
use **Info → Collection** to select a same-family collection or **No
collection**; do not edit `.paradev/meta.yaml`. The service previews the exact
metadata revision, applies only its plan hash, and refreshes the Catalog after
the atomic write. Python and CLI clients use the same operation:

```python
plan = project.set_module_collection("focus/FOCUS_DEMO", "C01_focus_tree")
project.set_module_collection(
    "focus/FOCUS_DEMO",
    "C01_focus_tree",
    write=True,
    plan_hash=plan["plan_hash"],
)
```

```bash
rtk uv run paradev module-collection-set projects/PIHC3 focus/FOCUS_DEMO --collection C01_focus_tree --json
# Review the payload, then pass its exact plan_hash:
rtk uv run paradev module-collection-set projects/PIHC3 focus/FOCUS_DEMO --collection C01_focus_tree --write --plan-hash <plan_hash> --json
```

Omit `--collection` to plan or apply clearing membership. Raw visible
`meta.yaml` remains under **Advanced metadata** only for exceptional author
choices such as `inactive` or `comment`.

Collection rename updates every explicit member pointer and moves the
descriptor through one durable transaction. It fails closed if a member has
conflicting visible and hidden collection metadata or a pointer that cannot be
edited safely; ParaDev will not leave dangling module references.
The module browser groups related families by authoring task and keeps
**Other & Advanced** collapsed until it is selected, so importer-only and
project-specific families do not dominate the normal workflow.

Family names, labels, navigation groups, and aliases are extension-owned
capabilities, not module metadata. The project keeps them in the hidden
`extensions/<family>/.paradev/meta.yaml` descriptor under
`meta.presentation`. You do not edit that file when creating content. Copying
a module folder, changing its `id - title`, definition, localization, and
image is enough to create another module instance. ParaDev's Registry supplies
the stable family id and grouping to the SDK, CLI, REST, MCP, Catalog browser,
and desktop—even while that family has no modules yet.

Tree and graph editors are also extension-owned. A registered
`ModuleDiagramProvider` declares its stable id and aliases, compatible build
families, desktop renderer, edit planner, optional node authoring kind, and
optional `scope_authoring_kind`. A
HeavenBase extension exposes it with `kind: paradev_diagram_provider`; a
project extension may set `replaces_registered_provider=True` to replace the
game-profile default atomically. The active binding appears in
`Project.browser()["families"][...]["diagram"]`, which is the source of truth
for SDK, REST, MCP, and desktop discovery. Clients must not maintain their own
list of focus, technology, doctrine, or MIO family ids.

PIHC3 activates all four current providers from its corresponding
`extensions/` folders. Focus declares
`scope_authoring_kind="collection"`, so the desktop discovers its **New
collection** action from the provider instead of recognizing the Focus
renderer by name. Focus uses collection-owned node authoring; technology
and doctrine use module authoring; MIO modules may expose several organization
trait trees. Project-exclusive graphs set `renderer="graph"` and return the
shared node/edge payload, so they render and submit guarded edits without a
new family branch in React or the SDK. Node ids must be unique; coordinates
must be finite pairs; edges must reference existing nodes and be unique by
kind/source/target. Editable nodes carry `source_revision`. ParaDev returns
generic `node_id` position intents and open-kind edge intents to the provider's
own planner, which remains responsible for source grammar and compilation.

Editable providers also declare `relationships`. Each action owns its open
intent `kind`, reader-facing label, shared canvas role, selected and
source-owning endpoints, symmetry, and one-or-many cardinality. The desktop
renders these declarations directly, including canvas picking and guarded
removal. Technology, Focus, Doctrine, and MIO therefore use the same control;
PIHC3-exclusive `renderer="graph"` providers can add relationship kinds without
a ParaDev family switch. One-cardinality actions replace the reviewed edge in
one draft, cross-scope endpoints and directed cycles fail closed, and the
provider planner remains the final source-safety authority.

When **Create** is opened from a selected graph node, the provider's
`selection_defaults` mapping pre-fills only declared template fields. In
PIHC3, a new technology inherits the selected folder, a lower grid position,
and a prerequisite; a doctrine inherits hidden layout and one reviewed path.
These values remain visible in the ordinary create form, changing one
invalidates its dry plan, and the exact scaffold plan is still reviewed before
one transaction writes it. Focus keeps the same behavior in its node-specific
dialog by preselecting both relative position and prerequisite.

Providers may instead expose `node_authoring` with a paired `node_plan`. This
is a small transport-neutral form plus selected-node mappings for adding an
item inside an existing module. PIHC3 MIO uses it: **Add graph item** on a
selected trait adds a child trait to that same organization, updates its
authoritative PDX definition and localization together, then rebuilds only the
MIO family. SDK, CLI, REST, MCP, and desktop send the same bounded
`node_intents` array (at most one item); it cannot be mixed with position or
edge intents. Apply requires the exact reviewed `plan_hash`. React contains no
MIO insertion or localization rules.

For a canonical PDX `def.txt`, **Guided** mode exposes existing simple
booleans, finite decimal numbers, quoted strings, and safe bare identifiers.
This applies generically to simple-source families such as ideas, characters,
events, and equipment. An extension may also declare an exact block-body or
integer-list control for a structure it owns; PIHC3 uses these for script
containers and map membership. ParaDev does not infer missing fields or
flatten undeclared blocks, conditions, variables, or colors. Use **Code** for
those structures.
When a large source has more controls than the bounded Guided view can show,
use the search box to request a smaller Registry projection. Search returns
complete matching sections, keeps each control's stable identity from the
full source, and never changes the draft. Clear the query to return to the
normal leading view. A no-results message means only that the current query
matched no safely editable control; the source remains available in **Code**.
Guided edits stay in the normal unsaved draft until **Apply** is chosen.
ParaDev replaces only the reviewed value token, preserves comments, spacing,
line endings, and surrounding source text, then reparses the draft before
another PDX field can be edited. Text fields accept normal multi-character
typing and commit once on blur or Enter; multiline controls commit on blur or
Command/Ctrl+Enter. Escape restores the previous value.
If the source changes underneath the form, Guided mode fails closed and asks
for a fresh projection instead of guessing a location.

### Clean up older metadata safely

Older modules may still repeat their folder-derived family as `type` in
`meta.yaml`. Review a cleanup plan first:

```bash
# Review one family, then apply that same scope with its exact returned hash.
rtk uv run paradev module-metadata-clean projects/PIHC3 --family idea --json
rtk uv run paradev module-metadata-clean projects/PIHC3 --family idea \
  --write --plan-hash FAMILY_PLAN_HASH --json

# Review one module, then apply that same scope with its exact returned hash.
rtk uv run paradev module-metadata-clean projects/PIHC3 --module idea/IDEA_SOURCE --json
rtk uv run paradev module-metadata-clean projects/PIHC3 --module idea/IDEA_SOURCE \
  --write --plan-hash MODULE_PLAN_HASH --json
```

The first command in each pair is a dry plan and never changes a file. Copy
its exact returned `plan_hash` into the matching apply command. ParaDev
removes only a plain top-level entry such as `type: idea` when it exactly
matches the module's folder family. It preserves authored fields such as
`title`, `collection`, and `settings`; invalid, ambiguous, or mismatched
metadata is reported instead of rewritten. If the reviewed files change
before apply, the stale hash is rejected. When cleanup would empty
`meta.yaml`, ParaDev removes the file if other authored module files keep the
module present. If `meta.yaml` is the module's only identity marker, ParaDev
keeps a minimal empty YAML object (`{}`) so the module does not disappear;
comment-only metadata also keeps an explicit `{}` so it remains valid YAML.

Current HoI4 families:

| Family | Output today |
| --- | --- |
| `focus` | Focus PDX, localization, optional collection view JSON. |
| `event` | Event PDX by namespace collection or object id. |
| `decision` | Decision category and decision PDX. |
| `idea` | Idea PDX, localization, icon copy, sprite GFX. |
| `modifier` | Modifier PDX and localization. |
| `opinion_modifier` | Opinion modifier PDX and localization. |
| `trait` | Trait PDX routed by the Registry-owned source default, with an advanced explicit subtype only for exceptions. |

Collections are used when sibling modules need shared output. Examples:

- focus tree: many `focus` modules in one tree;
- event namespace: many `event` modules in one event file;
- decision category: many decisions under one category.

Define new hand-authored families in Python through `python_modules`; use
`CollectionSourceFamily` when the collection descriptor owns shared sources such as an
event namespace header or collection localization. See [developer-manual.md](developer-manual.md)
for executable module-family and collection-family examples.

A collection descriptor is also a folder:

```text
src/collections/focus/C01_NEW - 新国策树/
  def.txt
```

For PIHC3, create a complete collection from a registered collection template.
The desktop **New collection** action appears for every family that publishes
one. Focus asks only for the logical id, readable title, and country tag.
Decision publishes the same contract for a decision category, asking for its
id, title, description, game icon id, and language. Both flows preview the
exact folder and files before applying the reviewed transaction; no visible
`meta.yaml` is required.

```python
from paradev.sdk import Project

project = Project.load("projects/PIHC3")
plan = project.scaffold_collection(
    "pihc3:focus-tree/basic",
    "C01_NEW",
    values={"title": "新国策树", "country_tag": "C01"},
)
project.scaffold_collection(
    "pihc3:focus-tree/basic",
    "C01_NEW",
    values={"title": "新国策树", "country_tag": "C01"},
    write=True,
    plan_hash=plan["plan_hash"],
)
```

```bash
rtk uv run paradev collection-scaffold projects/PIHC3 \
  pihc3:focus-tree/basic C01_NEW \
  --value "title=新国策树" --value "country_tag=C01" --json
rtk uv run paradev collection-scaffold projects/PIHC3 \
  pihc3:focus-tree/basic C01_NEW \
  --value "title=新国策树" --value "country_tag=C01" \
  --write --plan-hash PLAN_HASH --json
```

Use `Project.templates(kind="collection")` or
`paradev templates --kind collection` to discover valid collection templates.
The first scaffold call is always a dry plan. Apply requires its exact
`plan_hash`; a changed source tree or destination blocks the write.

`collection-create` is the low-level fallback for a family that has no
registered collection template. It creates only a descriptor metadata folder:

```bash
rtk uv run paradev collection-create projects/starter-mod event germany \
  --metadata "title=Germany Events" \
  --write \
  --json
```

Add expected descriptor source files with `collection-edit --create`. Normal
PIHC3 users should not need this metadata-only path.

Read or replace one descriptor text file with the collection file commands:

```bash
rtk uv run paradev collection-file projects/starter-mod germany category.txt --family event --json
rtk uv run paradev collection-edit projects/starter-mod germany category.txt \
  --family event \
  --text "add_namespace = germany" \
  --json
```

`collection-edit` preserves exact text. Use `--family` or `--source-root` when the same collection id exists in more than one descriptor family or source root.

Rename a descriptor folder when the collection id needs to change:

```bash
rtk uv run paradev collection-rename projects/starter-mod germany france --family event --json
```

ParaDev moves the descriptor folder and rewrites every explicit
`collection: germany` pointer in its member modules as one crash-recoverable
transaction. Both visible `meta.yaml` and hidden `.paradev/meta.yaml` pointers
are supported; unrelated metadata and hidden settings are preserved. Authored
PDX identifiers, localization keys, and generated artifacts are not rewritten.

Plan descriptor cleanup before deleting it:

```bash
rtk uv run paradev collection-remove projects/starter-mod germany --family event --json
rtk uv run paradev collection-remove projects/starter-mod germany --family event --write --plan-hash HASH_FROM_PLAN --json
```

The first command inventories the descriptor and shows the modules that will be preserved and ungrouped. The second command applies that exact plan: it clears explicit `collection: germany` pointers in visible and hidden metadata, preserves unrelated settings, and removes `src/collections/event/germany` in one crash-recoverable transaction. It never cascades into module deletion.

Inspect the actual source files owned by a descriptor:

```bash
rtk uv run paradev sources projects/starter-mod --collection germany --owner-kind collection --json
```

Use this for descriptor panes. Omit `--owner-kind collection` when you want all module source files associated with that collection id.

Source slots are files a family knows how to consume. Built-in slot kinds include:

| Kind | Example | Meaning |
| --- | --- | --- |
| `pdx` | `def.txt` | Parsed as PDX script. |
| `loc` | `main.loc` | Parsed as localization entries. |
| `copy` | `icon.dds` | Copied as a static artifact; ParaDev maintains deterministic and exact-byte hashes automatically. |

Project-local families can be declared in `paradev.yaml` when the built-in families are not enough. Use [Developer Manual](developer-manual.md) for that path.

Authoring templates are separate from build families. A family says how ParaDev compiles a module or collection; an authoring template creates the starter source files for a new instance. Use `Project.templates()`, `Project.scaffold_module(...)`, and `Project.scaffold_collection(...)` from Python, or `paradev templates`, `paradev scaffold`, and `paradev collection-scaffold` from the CLI. Every template declares `kind: module` or `kind: collection`. Project-local authoring templates live at top-level `templates` in `paradev.yaml`; their optional `directory` format defaults to `{object_id}` and can opt into a readable physical name such as `{object_id} - {title}`. Family artifact templates live under `families.<family>.templates`, and the derived `Project.families()["families"][...]["outputs"]` rows describe the artifact types, owner scope, and target roots they can plan. Template rows expose `args` plus a GUI-ready `form.fields` list, so clients can render one generic popup form for built-in, project-local, or Python-backed templates. Scaffold and batch payloads retain the logical id and report the resolved physical directory as `folder_name`. Template rows also expose their renderer kind and the family `default_assets` available to the template, but scaffold does not copy those defaults into the instance folder. Default assets are family-level metadata until a user explicitly authors or edits an instance asset. Family rows also split metadata into `common_keys` and `family_keys`, with `unknown_key_policy` showing how loose and strict builds report unknown keys; `comment` is a shared optional metadata key for module and collection notes. A template is ready to scaffold only when its `family` is registered. `Project.templates()` marks that with `authoring_ready`; rows that are not ready include `template.unknown_family`. The same response includes an `index` so tools can find templates by id, kind, family, source, readiness, or diagnostic code, and the same fields can be used as exact filters.

A template should use `directory: "{object_id} - {title}"` and normally omit
`meta.yaml`. It may keep a user-facing `collection`, `inactive`, or `comment`
there. Trusted extension templates may declare SDK-owned `system_files` under
`.paradev/`; those files participate in the same guarded scaffold transaction
but are excluded from the ordinary template file list and raw novice editing.
PIHC3 uses that system-file path for Focus-tree membership and migrated
Modifier output grouping. Users select the tree/group through the owning
workflow; they do not maintain routing YAML by hand.

When one existing folder uniquely represents the requested logical id, a
fresh plan reuses it so scaffold remains idempotent across readable suffixes.
Multiple aliases, case-only collisions, and Unicode NFC-equivalent collisions
block the plan. The module-local `.paradev/` directory is reserved for system
metadata and is ignored by scaffold's existing-content comparison. A fresh
scaffold creates only the system files explicitly declared by its trusted
extension template.

Use `Project.create_modules(...)` when a person, importer, or LLM agent needs to create several template-backed modules as one guarded operation. Every request row supplies `object_id`, `values`, and exactly one of `family`, `template_id`, or `family_or_template`. The method plans by default and returns a state-sensitive `plan_hash`; applying the batch requires that exact hash:

```python
from paradev.sdk import Project

project = Project.load("projects/starter-mod")
requests = [
    {"family": "idea", "object_id": "IDEA_A", "values": {"title": "Idea A"}},
    {"family": "idea", "object_id": "IDEA_B", "values": {"title": "Idea B"}},
]
plan = project.create_modules(requests)
result = project.create_modules(requests, write=True, plan_hash=plan["plan_hash"])
```

The CLI accepts the same rows in a JSON object with a `modules` array:

```bash
rtk uv run paradev module-batch-create projects/starter-mod --request module-batch.json --json
rtk uv run paradev module-batch-create projects/starter-mod --request module-batch.json --write --plan-hash PLAN_HASH --json
```

To start from an existing PIHC3 module, use **Duplicate** in the desktop editor
or `Project.duplicate_module(...)`. Duplication also plans first. By default,
the selected Registry family rewrites owned path names and exact identifier
tokens in UTF-8 source files from the old object id to the new one. Images and
other binary assets remain byte-for-byte identical. The review shows the
projected target paths, target hashes, rewritten-file count, and renamed-path
count before anything is written. The module-local `.paradev/` system
directory is excluded:

```bash
rtk uv run paradev module-duplicate projects/PIHC3 idea/IDEA_SOURCE IDEA_NEW --json
rtk uv run paradev module-duplicate projects/PIHC3 idea/IDEA_SOURCE IDEA_NEW --write --plan-hash PLAN_HASH --json
```

Use `--identity preserve` only when an exact path-and-byte copy is explicitly
needed. A family may replace or disable the identity rewriter through its
Registry definition; the SDK and desktop contain no family-specific rewrite
switch. There is no overwrite or force mode. The destination must remain
absent and both the source inventory and projected target must still match the
reviewed `plan_hash`.

The desktop **Assets** tab follows the same Registry contract for copied
images, models, and other binary resources. A family with one valid authoring
destination places a new file automatically. For aggregate PIHC3 families such
as `interface` or `ui`, ParaDev lists the existing folders owned by the matching
copy slot and asks which one should receive the file. If no existing folder
matches, the file remains a blocked draft until an advanced project-relative
path inside that module passes Registry validation. Use the row-level
**Replace** action for an existing file; ParaDev will not guess between
duplicate basenames or silently overwrite an existing resource.

Run `paradev mcp serve` as a standard stdio MCP server for agent authoring. The bounded HeavenBase toolkit exposes `project_templates` first for valid templates, source roots, and form fields; `project_authoring_path` and `project_authoring_plan` for destination and source-slot preflight; `project_browser` plus `module_file` or `collection_file` for Registry-owned source discovery and stable `size`/`mtime_ns` text snapshots; `module_asset` for bounded Registry-owned copy/image resources; `project_create_modules` for guarded template-backed batches; `collection_scaffold` for complete registered collections such as PIHC3 focus trees; `localization_workspace` and `localization_plan` for modules and collections; and module duplicate, membership, metadata cleanup, and diagram read/edit tools.

The desktop **Agents** page removes installation-path guesswork. In a source
checkout it shows the exact `uv` program, arguments, and working directory used
by the app. In an installed build it shows the bundled backend executable that
forwards `mcp serve` and the resolved bundled `$paradev-authoring` `SKILL.md`.
Copy those returned values into your MCP-capable agent instead of assuming that
`paradev` is globally available on `PATH`. ParaDev AI uses the same templates
inside the app and always opens its proposed module batch for review before a
write.

For an existing module or collection edit, pass the `module_file` or
`collection_file` revision back to
`project_draft_apply` as `expected_size` and `expected_mtime_ns`. ParaDev then
rejects the draft if another editor changed the source after the agent read it.
Related source edits and a readable-folder rename can share that one
transaction. SDK, CLI, REST, frontend, and MCP callers receive the same
canonical payloads.

For an image or other copied resource, locate the exact slot path through
`project_browser`, then call `module_asset` without `include_content` first.
The result identifies the owning Registry slots, digest, and stable
`draft_guard`. Request base64 only when the bytes are actually needed. To
replace the asset, pass that guard unchanged with the new `content_base64` in
the same `project_draft_apply` transaction as related text edits. PNG-to-DDS
conversion may additionally set the existing `content_format` and
`target_format` pair. A stale guard rejects the complete draft.

Use `paradev` as the MCP client command and `["mcp", "serve"]` as its arguments. The server writes only MCP frames to stdout; warnings and errors remain on stderr.

For programmatic embedding, call `create_authoring_mcp_server()` to obtain
the same FastMCP server with ParaDev's exact authoring schemas preserved.

There is intentionally no force mode. ParaDev stages the complete batch before publishing any file, holds the source mutation lock while it revalidates the plan, and never overwrites an existing target. A changed project, stale hash, duplicate request, divergent existing module, or concurrent target injection blocks the whole batch. If every requested module already matches an explicit fresh plan, apply is a no-op. This provides exception- and concurrency-safe creation; like ordinary filesystem publication, it cannot promise a portable multi-directory single-syscall commit across process or machine failure.

## 中文

用户需要理解的模型很小：

1. 一个项目包含多个模块。
2. 某些模块会被组织进集合。
3. 构建 profile 把模块和集合变成 artifacts。

模块就是一个目录：

```text
src/modules/idea/GER_industry_spirit/
  meta.yaml（可选）
  def.txt
  main.loc
  icon.dds
```

逻辑 module id 是 `family/object_id`。物理目录默认使用 `object_id`，项目模板也可以添加便于阅读的后缀。当你要移动这个源模块容器时，使用 rename：

```bash
rtk uv run paradev module-rename projects/starter-mod modifier/starter_mod_starter_modifier starter_mod_renamed_modifier --json
```

这只会修改 ParaDev 的 module id 和目录路径。如果目录名带有
`TECHNOLOGY_FIREARM_I - Basic Firearms` 这样的可读后缀，rename 会保留该
后缀。它不会改写 `def.txt` 里的 HoI4 id、本地化 key 或其他作者文件。

桌面端的模块与 collection 共用同一个 Registry 管理的本地化表。选择 Decision
类别、Focus tree 或其他 collection 时，会得到与普通模块相同的语言、key、覆盖率
和受保护编辑流程；作者无需因为文本属于 collection 就手工打开或合并 `.loc`
文件。SDK 使用统一的区分式目标：`target_kind="module"` 或
`target_kind="collection"`，配合 `target_id` 和可选 `family`。返回的 workspace
与 plan 通过 `target.kind`、`target.id`、`target.family`、`target.object_id`
标识源单元，每个来源使用 `unit_relative_path`。REST 与 MCP 接收相同字段；plan
始终只读，只有显式应用返回的 source edits 才会写入文件。

删除模块前先执行计划：

```bash
rtk uv run paradev module-remove projects/starter-mod modifier/starter_mod_starter_modifier --json
rtk uv run paradev module-remove projects/starter-mod modifier/starter_mod_starter_modifier --write --json
```

第一条命令返回 `paradev.module.remove.v1` 和将删除的文件清单，但保留目录。第二条命令只删除模块源目录，不会触碰已经生成的 build artifacts。

GUI、导入器或脚本需要类似编辑器的访问时，可以读取或替换单个文本源文件：

```bash
rtk uv run paradev module-file projects/starter-mod modifier/starter_mod_starter_modifier def.txt --json
rtk uv run paradev module-edit projects/starter-mod modifier/starter_mod_starter_modifier def.txt \
  --text "starter_mod_starter_modifier = { stability_factor = 0.10 }" \
  --json
```

`module-edit` 会保留传入的精确文本。只有在已有模块目录内新增文件时才使用 `--create`。

导入器或迁移脚本一次生成多个模块文本更新时，使用 `module-batch-edit`。请求 JSON 包含 `edits` 数组，并可在顶层设置 `create` 和 `encoding` 默认值；每个 edit 使用 `module_id`、`relative_path` 和 `text`，并可选 `source_root`、`create`、`encoding` 覆盖。Python 中用 `Project.module_batch_edit_request(...)` 生成规范请求，CLI 中用 `paradev module-batch-request` 生成规范请求，然后交给 `module-batch-edit`；请求生成会校验每个目标模块已经存在，并要求缺失文件显式选择创建。规范请求包含 `summary`，其中有模块数量、已有/缺失目标数量、会变化/不会变化的目标数量、允许创建的行数和不同编码数量，方便生成器在应用前报告预检影响；同时包含逐 edit 的 `targets` 数组和 `target_index`，记录项目相对目标路径、已有/新建/变化标记、create 模式、encoding 和编码后的字节数，导入器和 GUI 预览无需应用请求即可检查具体目标。添加 `--dry-run` 可以在写入前校验并预览解析后的文件目标。JSON 响应包含 `created_count`、`updated_count` 和每个文件的 `created` 标记，调用方可以区分新的迁移产物和已有模块更新；也包含 `changed_count`、`unchanged_count` 和每个文件的 `changed` 标记，便于可重复运行的迁移脚本报告无需改写的目标而不必重新扫描文件。纯文本 CLI 输出会在摘要行同时报告改写/未改写和新增/更新数量。写入模式下，未变化的目标仍会被校验并出现在响应中，但不会重新写入对应文件。

```python
from paradev.sdk import Project

project = Project.load("projects/PIHC3")
request = project.module_batch_edit_request(
    [
        {
            "module_id": "technology/TECHNOLOGY_AIR_CLOUDSHIP",
            "relative_path": "migration/notes.txt",
            "text": "generated\n",
        }
    ],
    create=True,
)
project.write_module_files(request["edits"], create=request["create"], encoding=request["encoding"], write=False)
```

```bash
rtk uv run paradev module-batch-request projects/PIHC3 --create --edit-json '{"module_id":"technology/TECHNOLOGY_AIR_CLOUDSHIP","relative_path":"migration/notes.txt","text":"generated\n"}' > batch-edits.json
rtk uv run paradev module-batch-edit projects/PIHC3 --request batch-edits.json --dry-run --json
rtk uv run paradev module-batch-edit projects/PIHC3 --request batch-edits.json --json
rtk uv run paradev module-batch-edit projects/PIHC3 --request-json '{"edits":[{"module_id":"technology/TECHNOLOGY_AIR_CLOUDSHIP","relative_path":"migration/notes.txt","text":"generated\n","create":true}]}' --json
rtk uv run python scripts/generate_batch_edits.py | rtk uv run paradev module-batch-edit projects/PIHC3 --request - --json
```

大多数模块不需要可见的 `meta.yaml`。只有目录、定义、本地化和图片无法表达的
重要选择才写入，例如：

```yaml
inactive: true
# comment: 说明为什么有意禁用该模块。
```

ParaDev 会从 `src/modules/<family>/` 推断系列，从目录前缀推断模块 ID，并把
`id - 首选语言标题` 的后缀作为显示标题。不要用 `type` 重复系列，也不要用
`title` 重复目录标题。设置 `inactive: true` 即可让模块退出所有构建；不要再建
第二棵 `inactive_modules/` 目录。SDK 自动维护的默认值、索引与导入状态放在模块
内隐藏的 `.paradev/` 下。collection membership 也属于 SDK 维护的隐藏状态。
桌面编辑器中请在**信息 → 合集**选择同 family collection，或选择**不属于合集**；
不要直接编辑 `.paradev/meta.yaml`。该操作先预览精确 metadata revision，只接受
对应 plan hash，再原子写入并刷新 Catalog。Python 与 CLI 使用同一个
`Project.set_module_collection(...)` / `module-collection-set` 两阶段操作；CLI
省略 `--collection` 即表示清除 membership。可见的原始 `meta.yaml` 只在
**高级元数据**中用于 `inactive` 或 `comment` 等少数作者选择。
collection rename 会在同一个持久事务中改写每个显式 member pointer 并移动
descriptor。若 member 的可见与隐藏 collection metadata 冲突，或 pointer 无法
安全编辑，操作会 fail closed；ParaDev 不会留下悬空的 module reference。
模块浏览器会按创作任务对系列分组，并默认收起**其他与高级**；选中其中的系列
时会自动展开，因此导入器专用和项目特有系列不会干扰日常工作流。

系列的稳定 id、标签、导航分组与 alias 属于 extension 能力，不属于每个模块的
元数据。项目在隐藏的
`extensions/<family>/.paradev/meta.yaml` 中通过 `meta.presentation` 保存它们。
创建内容时不需要编辑该文件：复制模块目录，修改 `id - 标题`、定义、本地化和
图片，就能得到新的模块实例。ParaDev Registry 会把同一系列身份提供给 SDK、
CLI、REST、MCP、Catalog 与桌面；即使该系列目前没有模块，也仍然可以创建。

树和图编辑器同样由 extension 所有。注册的 `ModuleDiagramProvider` 声明稳定
id 与 alias、兼容的 build family、桌面 renderer、编辑 planner，以及可选的
authoring kind。HeavenBase extension 通过
`kind: paradev_diagram_provider` 暴露 provider；项目 extension 可以设置
`replaces_registered_provider=True`，原子替换游戏 profile 的默认实现。
当前绑定会出现在
`Project.browser()["families"][...]["diagram"]`，它是 SDK、REST、MCP 与桌面
发现能力的唯一事实来源。客户端不应再自行维护 focus、technology、doctrine
或 MIO family id 列表。

PIHC3 目前四个 provider 都位于各自的 `extensions/` 文件夹。Focus 使用
collection-owned node authoring；technology 与 doctrine 使用 module
authoring；一个 MIO module 可以公开多棵 organization trait tree。PIHC3
专属图类型可设置 `renderer="graph"` 并返回通用 node/edge payload，因此无需在
React 或 SDK 中新增 family 分支，也能渲染并提交受保护的编辑。Node id 必须唯一；
坐标必须成对且为有限数字；edge 必须指向现有 node，并按
kind/source/target 唯一。可编辑 node 需要携带 `source_revision`。ParaDev 会把
通用 `node_id` 位置 intent 和开放 kind 的 edge intent 交还 provider 自己的
planner；源语法与编译规则仍完全归该 provider 所有。

可编辑 provider 还会声明 `relationships`。每个 action 自己拥有开放的 intent
`kind`、面向用户的标签、共享画布角色、当前选中端点与源码所有端点、是否对称，
以及一对一或一对多 cardinality。桌面会直接渲染这些声明，包括画布点选与受保护
的删除。因此 technology、Focus、Doctrine 与 MIO 共用同一套控件；PIHC3 专属
的 `renderer="graph"` provider 也能增加关系类型，而无需在 ParaDev 中增加
family 分支。一对一 action 会在同一 draft 中替换已审阅 edge；跨 scope 端点与
有向环会关闭失败，provider planner 仍是源码安全的最终权威。

从已选图节点打开**创建**时，provider 的 `selection_defaults` 映射只会预填
其明确声明的 template 字段。在 PIHC3 中，新 technology 会继承当前 folder、
更低一行的坐标与 prerequisite；doctrine 会继承隐藏布局和一条已审阅 path；
新 MIO organization 的初始可编辑 trait 会继承更低的起始位置。这些值仍会
显示在普通创建表单中，任何修改都会使旧 dry plan 失效，并且写入前仍须审阅
精确 scaffold plan。Focus 的专用节点对话框采用同一体验，会预选相对位置与
prerequisite。React 不保存任何 family-specific 默认规则。

大型 `def.txt` 的安全控件超过 Guided 的有界显示上限时，可以使用搜索框请求
更小的 Registry 投影。搜索会返回完整的匹配 section，并保留控件在完整源文件中
的稳定身份；它不会修改草稿。清空搜索即可回到默认的前部视图。没有结果只表示
当前关键词没有匹配到可安全编辑的控件，完整源文件仍可在**代码**模式中编辑。

### 安全清理旧版元数据

旧模块的 `meta.yaml` 可能仍然用 `type` 重复目录已经表达的系列。请先查看清理
计划：

```bash
# 查看一个系列，再用它返回的完整 hash 应用同一范围。
rtk uv run paradev module-metadata-clean projects/PIHC3 --family idea --json
rtk uv run paradev module-metadata-clean projects/PIHC3 --family idea \
  --write --plan-hash FAMILY_PLAN_HASH --json

# 查看一个模块，再用它返回的完整 hash 应用同一范围。
rtk uv run paradev module-metadata-clean projects/PIHC3 --module idea/IDEA_SOURCE --json
rtk uv run paradev module-metadata-clean projects/PIHC3 --module idea/IDEA_SOURCE \
  --write --plan-hash MODULE_PLAN_HASH --json
```

每组的第一条命令都是 dry plan，绝不会修改文件。请把它返回的完整
`plan_hash` 复制到同组的应用命令。ParaDev 只会在 `type: idea` 这类简单顶层
字段与模块目录系列完全一致时删除它。`title`、`collection`、`settings` 等作者
字段会保留；无效、含糊或不匹配的 metadata 只会报告，不会重写。如果文件在
审阅后发生变化，过期 hash 会被拒绝。
若清理后 `meta.yaml` 为空，而其他作者文件仍能保持模块存在，ParaDev 会删除
这个空文件；若 `meta.yaml` 是模块唯一的身份标记，ParaDev 会保留最小的
空 YAML 对象（`{}`），避免模块消失。仅含注释的 metadata 也会保留显式
`{}`，确保 YAML 仍然有效。

当前 HoI4 families：

| Family | 当前输出 |
| --- | --- |
| `focus` | 国策 PDX、本地化、可选集合视图 JSON。 |
| `event` | 按 namespace collection 或 object id 输出事件 PDX。 |
| `decision` | 决议类别和决议 PDX。 |
| `idea` | Idea PDX、本地化、图标复制、sprite GFX。 |
| `modifier` | Modifier PDX 和本地化。 |
| `opinion_modifier` | Opinion modifier PDX 和本地化。 |
| `trait` | 由 Registry 所属的 source default 路由；只有例外类型才需要 advanced 显式 subtype。 |

当兄弟模块需要共享输出时使用集合。例子：

- 国策树：多个 `focus` 模块合成一棵树；
- 事件 namespace：多个 `event` 模块合成一个事件文件；
- 决议类别：多个 decision 放在同一个 category 下。

新增手写 family 时，通过 `python_modules` 使用 Python 定义；当 collection
descriptor 自己拥有共享源文件，例如事件 namespace header 或 collection
localization 时，使用 `CollectionSourceFamily`。可执行的 module-family 和
collection-family 示例见 [developer-manual.md](developer-manual.md)。

集合 descriptor 也是目录：

```text
src/collections/focus/C01_NEW - 新国策树/
  def.txt
```

PIHC3 应优先通过已注册的 collection template 创建完整集合。桌面端的
**新建国策树**也使用同一套通用契约：用户只需填写逻辑 ID、可读标题和国家
tag，确认精确目录与文件计划后再应用事务。模板直接写入集合拥有的 `def.txt`，
不需要可见的 `meta.yaml`。

```python
from paradev.sdk import Project

project = Project.load("projects/PIHC3")
plan = project.scaffold_collection(
    "pihc3:focus-tree/basic",
    "C01_NEW",
    values={"title": "新国策树", "country_tag": "C01"},
)
project.scaffold_collection(
    "pihc3:focus-tree/basic",
    "C01_NEW",
    values={"title": "新国策树", "country_tag": "C01"},
    write=True,
    plan_hash=plan["plan_hash"],
)
```

```bash
rtk uv run paradev collection-scaffold projects/PIHC3 \
  pihc3:focus-tree/basic C01_NEW \
  --value "title=新国策树" --value "country_tag=C01" --json
rtk uv run paradev collection-scaffold projects/PIHC3 \
  pihc3:focus-tree/basic C01_NEW \
  --value "title=新国策树" --value "country_tag=C01" \
  --write --plan-hash PLAN_HASH --json
```

用 `Project.templates(kind="collection")` 或
`paradev templates --kind collection` 查询可用模板。第一步永远只生成计划，
应用时必须传回完全一致的 `plan_hash`；源树或目标发生变化会阻止写入。

`collection-create` 是没有已注册 collection template 时使用的底层后备接口。
它只创建 descriptor metadata 目录：

```bash
rtk uv run paradev collection-create projects/starter-mod event germany \
  --metadata "title=Germany Events" \
  --write \
  --json
```

期望的 descriptor 源文件继续用 `collection-edit --create` 添加。普通 PIHC3
用户不应需要这条只创建 metadata 的路径。

用 collection file 命令读取或替换一个 descriptor 文本文件：

```bash
rtk uv run paradev collection-file projects/starter-mod germany category.txt --family event --json
rtk uv run paradev collection-edit projects/starter-mod germany category.txt \
  --family event \
  --text "add_namespace = germany" \
  --json
```

`collection-edit` 会保留精确文本。当同一个 collection id 存在于多个 descriptor family 或 source root 中时，使用 `--family` 或 `--source-root` 消除歧义。

collection id 需要调整时，可以重命名 descriptor 目录：

```bash
rtk uv run paradev collection-rename projects/starter-mod germany france --family event --json
```

ParaDev 会在同一个可崩溃恢复的事务中移动 descriptor 目录，并把 member 模块可见或隐藏 metadata 中显式的 `collection: germany` 改为 `collection: france`。本地化 key、作者维护的 PDX 标识符和生成 artifacts 不会改写。

删除 descriptor 前先做计划：

```bash
rtk uv run paradev collection-remove projects/starter-mod germany --family event --json
rtk uv run paradev collection-remove projects/starter-mod germany --family event --write --plan-hash PLAN_返回的_HASH --json
```

第一条命令会列出 descriptor 文件，以及将被保留并解除分组的模块。第二条命令应用该精确计划：清除可见/隐藏 metadata 中显式的 `collection: germany`，保留无关设置，并在同一个可崩溃恢复的事务中删除 `src/collections/event/germany`；它绝不会级联删除模块。

查看 descriptor 自己拥有的实际源文件：

```bash
rtk uv run paradev sources projects/starter-mod --collection germany --owner-kind collection --json
```

descriptor 面板使用这条命令。需要查看同一 collection id 关联的所有模块源文件时，去掉 `--owner-kind collection`。

Source slot 是 family 会消费的文件。内置 slot kind 包括：

| Kind | 示例 | 含义 |
| --- | --- | --- |
| `pdx` | `def.txt` | 按 PDX 脚本解析。 |
| `loc` | `main.loc` | 按本地化条目解析。 |
| `copy` | `icon.dds` | 作为静态 artifact 复制；ParaDev 会自动维护确定性 hash 和精确字节 hash。 |

当内置 family 不够用时，可以在 `paradev.yaml` 中声明项目本地 family。这个路径见 [开发者手册](developer-manual.md)。

创建模板和构建 family 是两件事。family 描述 ParaDev 如何编译模块或集合；创建模板负责为新实例生成起始源文件。可以在 Python 中使用 `Project.templates()`、`Project.scaffold_module(...)` 和 `Project.scaffold_collection(...)`，也可以在 CLI 中使用 `paradev templates`、`paradev scaffold` 和 `paradev collection-scaffold`。每个模板都声明 `kind: module` 或 `kind: collection`。项目本地创建模板写在 `paradev.yaml` 顶层 `templates`；其可选 `directory` 格式默认是 `{object_id}`，也可以显式采用 `{object_id} - {title}` 这样的可读物理目录名。family 的 artifact 模板写在 `families.<family>.templates` 下面，派生出的 `Project.families()["families"][...]["outputs"]` 行会描述它能计划的 artifact type、owner 范围和 target root。模板行会暴露 `args` 和可直接渲染弹窗表单的 `form.fields`，所以 GUI 可以用同一个通用组件处理内置、项目本地和 Python-backed 模板。Scaffold 和 batch payload 保留逻辑 id，并用 `folder_name` 返回解析后的物理目录。模板行也会暴露 renderer 类型和该 family 可用的 `default_assets`，但 scaffold 不会把这些默认资源复制进实例目录；默认资源只是 family 级别 metadata，直到用户显式创建或编辑实例资源。Family 行也会把 metadata 拆成 `common_keys` 和 `family_keys`，并用 `unknown_key_policy` 说明 loose 与 strict build 如何报告未知 key；`comment` 是模块和集合都可用的可选备注 metadata。只有模板指向的 `family` 已注册时，才能执行 scaffold。`Project.templates()` 用 `authoring_ready` 标记这一点；未就绪的行会包含 `template.unknown_family`。同一个响应还包含 `index`，工具可以按 id、kind、family、source、readiness 或 diagnostic code 找到模板，也可以用这些字段做精确过滤。

模板可以完全省略 `meta.yaml`，也可以只写 `title` 等真正由作者填写的字段；
不应重复 typed destination path 已经携带的 family。

当一个已有目录能够唯一代表请求的逻辑 id 时，新计划会复用它，因此带可读
后缀的 scaffold 仍然幂等。多个 alias、仅大小写不同的冲突，以及 Unicode
NFC 等价冲突都会阻止计划。模块内的 `.paradev/` 是系统 metadata 保留目录，
scaffold 比较已有内容时会忽略它。全新 scaffold 只会创建可信 extension
template 显式声明的 system files。

当用户、导入器或 LLM agent 需要把多个 template-backed module 作为一个受保护操作创建时，使用 `Project.create_modules(...)`。每一行请求都要提供 `object_id`、`values`，并且只能在 `family`、`template_id`、`family_or_template` 中选择一个。该方法默认只生成计划并返回与当前状态绑定的 `plan_hash`；应用批次时必须传回完全一致的 hash：

```python
from paradev.sdk import Project

project = Project.load("projects/starter-mod")
requests = [
    {"family": "idea", "object_id": "IDEA_A", "values": {"title": "Idea A"}},
    {"family": "idea", "object_id": "IDEA_B", "values": {"title": "Idea B"}},
]
plan = project.create_modules(requests)
result = project.create_modules(requests, write=True, plan_hash=plan["plan_hash"])
```

CLI 接收相同的 rows，JSON 对象顶层使用 `modules` 数组：

```bash
rtk uv run paradev module-batch-create projects/starter-mod --request module-batch.json --json
rtk uv run paradev module-batch-create projects/starter-mod --request module-batch.json --write --plan-hash PLAN_HASH --json
```

如果要从现有 PIHC3 模块开始，可以在桌面编辑器中使用 **Duplicate**，
或调用 `Project.duplicate_module(...)`。复制同样先生成计划。默认情况下，
所选 Registry family 会把所属路径名及 UTF-8 源文件中的精确标识 token
从旧 object id 改写为新 id；图片等二进制资源仍保持逐字节一致。审阅界面会
在写入前显示目标路径、目标 hash、改写文件数及改名路径数。模块内的
`.paradev/` 系统目录不会复制：

```bash
rtk uv run paradev module-duplicate projects/PIHC3 idea/IDEA_SOURCE IDEA_NEW --json
rtk uv run paradev module-duplicate projects/PIHC3 idea/IDEA_SOURCE IDEA_NEW --write --plan-hash PLAN_HASH --json
```

只有明确需要路径和内容完全不变的副本时，才使用
`--identity preserve`。Family 可以在自己的 Registry 定义中替换或停用
identity rewriter；SDK 与桌面端不维护 family-specific rewrite switch。
该操作没有 overwrite 或 force 模式。目标必须保持不存在，而且源文件
inventory 与预计目标都必须仍与已审阅的 `plan_hash` 一致。

运行 `paradev mcp serve` 即可启动标准 stdio MCP authoring server。这个有明确边界的 HeavenBase toolkit 先通过 `project_templates` 提供有效 template、source root 和 form field；通过 `project_authoring_path` 与 `project_authoring_plan` 预检目标目录和 source slot；通过 `project_browser` 与 `module_file` 或 `collection_file` 按 Registry contract 定位现有源文件，并读取同一稳定快照中的 `size`、`mtime_ns` 与文本；通过 `module_asset` 有界读取 Registry 所属的 copy/image 资源；通过 `project_create_modules` 创建受保护的 template batch；通过 `collection_scaffold` 创建 PIHC3 国策树这类完整注册集合；通过 `localization_workspace` 与 `localization_plan` 编辑 module 或 collection 的本地化；并提供 module duplicate、membership、metadata cleanup 与 diagram read/edit 工具。

桌面端的 **智能体** 页面无需你猜测安装路径。源码检出环境会显示应用实际使用的
`uv` 程序、参数与工作目录；安装版会显示能够转发 `mcp serve` 的内置后端可执行文件，
以及内置 `$paradev-authoring` 的 `SKILL.md` 确切路径。请把页面返回的值复制到支持
MCP 的智能体配置中，而不要假设全局 `PATH` 中一定存在 `paradev`。应用内的
ParaDev AI 使用同一批模板，并且写入前始终会把提议的批量模块方案打开供你检查。

编辑现有 module 或 collection 时，把 `module_file` 或 `collection_file`
返回的 revision 作为
`expected_size` 与 `expected_mtime_ns` 传回 `project_draft_apply`。如果其他
编辑器在 agent 读取后改动了源文件，ParaDev 会拒绝旧 draft。相关源文件编辑
与可读目录名 rename 可以共用一个事务。SDK、CLI、REST、frontend 与 MCP
caller 使用同一套 canonical payload。

对于图片或其他复制资源，先通过 `project_browser` 找到准确的 slot path，再在
不设置 `include_content` 的情况下调用 `module_asset`。返回值会标明 Registry
所属 slot、digest 和稳定的 `draft_guard`；只有确实需要原始字节时才请求
base64。替换资源时，把该 guard 原样与新的 `content_base64` 一起放进同一个
`project_draft_apply` transaction，并可同时提交相关文本修改。PNG 转 DDS
时还可使用已有的 `content_format` 与 `target_format` 成对字段。guard 过期会
拒绝整个 draft。

MCP client 的 command 使用 `paradev`，参数使用 `["mcp", "serve"]`。Server 的 stdout 只写 MCP frame；warning 与 error 保留在 stderr。

若要在 Python 中嵌入，可调用 `create_authoring_mcp_server()` 获取相同的
FastMCP server，并保留 ParaDev 完整、精确的 authoring schema。

这个接口刻意没有 force 模式。ParaDev 会在发布任何文件之前暂存完整批次，在重新校验计划时持有 source mutation lock，并且绝不覆盖已有目标。项目变化、过期 hash、重复请求、内容不同的已有 module 或并发注入目标都会阻止整个批次。如果所有请求的 module 都已经与一份显式的新计划完全一致，则 apply 是 no-op。它保证异常与并发场景下的安全创建；与普通文件系统发布一样，它无法跨进程崩溃或机器故障承诺可移植的多目录单系统调用提交。
