# PIHC3

## English

PIHC3 is the clean ParaDev project for migrating the PIHC mod lineage. It has a real project manifest, committed native source modules, and project-local Python families for PIHC-only compilation rules. The former machine-local `PIHC_dev` copy overlay has been removed; current builds use the committed PIHC3 source tree only.

Current status:

- normal mod authoring should still start with `paradev new`;
- load a current PIHC3 checkout by selecting its folder in ParaDev;
- normal navigation contains 51 visible semantic families, all with a
  project-local create template;
- the current contract has 70 registered compiler families plus the
  `localisation` postprocessor; the 2026-08-10 clean and cached publication
  smoke reports 14,574 active modules, 106 collections, 35,398 generated artifacts,
  zero diagnostics or errors, and `blocked: false`;
- the remaining 20 hidden module families preserve low-level HoI4 file domains while
  semantic consolidation continues; none is an `_asset_component`;
- all 71 project extension folders are HeavenBase 0.1.2.2 Registry modules;
  all 70 module types expose registered compiler families, 63 genuinely
  PIHC3-owned types also expose project-local `hb.Entity` classes, and the
  seven built-in HoI4 types use thin compiler overlays; `localisation` is a
  postprocessor rather than an Entity;
- module object identity comes from
  `src/modules/{family}/{object_id} - {preferred title}`; the title suffix is
  readable and the object-id prefix remains stable;
- PIHC-only behavior must stay out of `src/paradev/`;
- migration code should use project-local HeavenBase modules under
  `extensions/`, scripts, and notes under the PIHC3 project folder.

PIHC3 has no `legacy/`, `_component`, `_asset_component`, or
`inactive_modules/` source
directory. Images, GFX, localization, and definitions live in the semantic
module that owns them. A module may use the optional visible keys `inactive`
or `comment`; folder-derived titles and SDK-owned settings do not need to be
repeated there. Hidden provenance may remain under `.paradev/`, but it is not
a compilation source.
Country, Focus, State, and Strategic Region localization is now fully
co-located. Every one of the 67 country modules, 738 Focus modules, 902 State
modules, and 330 Strategic Region modules owns one `main.loc`; tree-wide Focus
text stays in the corresponding `src/collections/focus/` folder. State modules
also own the 910 victory-point names for provinces declared in their own
`def.txt`. Their project-local compiler families aggregate those module sources
back into HoI4's `state_names`, `victory_points`, and
`strategic_region_names` files, including safe module-partial builds. The
hidden `LOCALIZATION_REPLACEMENTS - 全局本地化覆盖` module contains only 141
intentional `localisation/replace` YAML files; it no longer duplicates any
ordinary Entity localization. Shared Doctrine reward text belongs to the
Doctrine support module, and Event translations belong to their Event module.
No live module repeats compiler settings in `.paradev/meta.yaml`. Trait routes,
doctrine subtype, equipment-designer ownership, state ids, and portable Entity
identity are derived by their project-owned Registry compilers from folder ids
and authored source. The remaining hidden module manifests contain only real
Focus Tree or Modifier collection membership.
Doctrine has one Registry family and one physical source root: 51 current
land/air doctrine modules compile their own definitions, while
`PIHC_DOCTRINE_SUPPORT - 教义共享支持` owns the shared folder, track, sea, and
Doctrine-reward localization files. The former `doctrine_definition` family
and 43 non-compiling pre-1.17 nodes are gone.

Current family taxonomy:

| Group | Count | Use |
| --- | ---: | --- |
| Template-backed semantic families | 51 | GUI/CLI/SDK create flows, including PIHC3-only entities such as inventory items, state lore, and superevents. |
| Hidden low-level file-domain families | 20 | Required HoI4 compatibility ownership kept out of novice navigation; these are concrete registered families, not asset sidecars. |

Visibility is declared by each standalone Registry extension, not by a central
family table in `paradev.yaml` and not by a GUI naming heuristic.

In the desktop editor, **Name** is the preferred-language localization title,
not a second metadata field. Applying a Name edit updates the concrete title
key resolved by the active Registry family and synchronizes the module folder
to `{object_id} - {portable title}`. ParaDev does not create a title-only
`meta.yaml`; existing `collection`, `inactive`, and `comment` metadata stays
untouched. PIHC3 keeps compiler routing such as Focus-tree membership and
legacy Modifier output grouping in hidden `.paradev/meta.yaml`; templates and
graph actions maintain it. The ordinary **Info → Collection** picker uses the
same guarded SDK transaction, so authors can assign or clear membership without
opening hidden files. The only visible module metadata in the live project is
the intentional `inactive: true` Bookmark flag.

PIHC3 declares `preferred_language: zh` once in `paradev.yaml`. Consequently,
every localization-bearing row returned by `Project.templates()` defaults to
Chinese in the compact desktop form, `Project.create_module(...)`, atomic
`Project.create_modules(...)` batches, REST, and MCP. Pass an explicit
`"language": "en"` only when a particular new module should be authored in
English. The preference is not copied into module metadata.

The English snippets in this section use `"language": "en"` when their
placeholder localization is intended to remain English. Omit that value for
normal PIHC3 authoring and ParaDev will emit Simplified Chinese localization.

Inspect the current creation surface:

```bash
rtk uv run paradev templates projects/PIHC3 --json
```

The current Registry returns 54 authoring-ready templates across 51 visible
families: 52 module templates plus the Focus-tree and Decision-category
collection templates. The normal user path is still one SDK call or one
compact GUI create form. PIHC3 templates use the preferred-language title in
the folder suffix, while defaults such as collection, category, costs,
identifiers, and language remain advanced fields. None of the 54 templates
creates visible `meta.yaml` or `meta.yml`; when a family needs system-owned
grouping, the guarded transaction maintains hidden `.paradev/meta.yaml`.

Build or dry-plan PIHC3 through the project-local one-line wrapper:

```bash
rtk uv run python projects/PIHC3/scripts/check_source_layout.py --json
rtk bash projects/PIHC3/compile.bash --json
rtk bash projects/PIHC3/compile.bash --clean --json
rtk bash projects/PIHC3/compile.bash --clean-only
rtk bash projects/PIHC3/compile.bash --summary --json
rtk bash projects/PIHC3/compile.bash --plan-only --json
rtk bash projects/PIHC3/compile.bash --family focus --summary --json
rtk bash projects/PIHC3/compile.bash --family focus --module FOCUS_C12_SHADOWS_OF_THE_PAST --summary --json
```

The source-layout command performs a no-write, machine-readable audit. Every wrapper build runs the same check quietly before discovery, rejecting retired component/legacy directories, symlink aliases, copy-marked paths, malformed or duplicate `id - title` units, empty units, loose family files, and user-visible system metadata. The first wrapper command writes generated artifacts and build manifests. It deliberately uses project-only publication, so compilation never reads or changes `PIHC3.mod` or its launcher ownership marker. The `--plan-only` form validates the same project through the current CLI without writing outputs. With `--family`, the module selector accepts the bare object id shown in the project browser; a repeated `focus/` prefix is optional. The wrapper enters the ParaDev repo root before resolving `uv`, so it works from any current directory.

Every path inside the Windows companion archive is limited to 200 UTF-16 code
units. This reserves 58 code units for the extraction destination, plus one
separator and the terminating null under the legacy 260-code-unit `MAX_PATH`
boundary, so common
Documents and OneDrive project locations do not depend on system-wide long-path
support. ParaDev must still validate the actual selected destination and show
an actionable shorter-location error when a user profile exceeds that budget.

For an isolated PIHC3 worktree, `PARADEV_ROOT=/path/to/ParaDev` selects the ParaDev source checkout only. The wrapper removes that selector before the CLI starts, preventing configuration files from being written into the source checkout. Set `PARADEV_CONFIG_ROOT=/path/to/isolated-config` separately only when the build should use an isolated ParaDev configuration root.
Set the absolute `PIHC3_MOD_ROOT=/path/to/mod` to redirect the PIHC3 output directory. The wrapper does not synchronize an external launcher descriptor.
`--clean` removes generated PIHC3 runtime data, Python bytecode caches, and the contents of the macOS HoI4 `PIHC3/` output directory before the build. It preserves the output directory itself and `PIHC3.mod`, keeping existing Paradox Launcher playsets bound to the same on-disk registration while compilation runs.
`--clean-only` performs the same cleanup without running a build and likewise preserves the launcher registration paths. Bytecode cleanup applies anywhere under the PIHC3 project tree while leaving the nested Git metadata alone.
`--summary` keeps the normal `paradev build` path but returns its compact
summary payload, so quick checks still publish artifacts without dumping the
full build plan.

The wrapper is a convenience surface, not a separate compiler. Direct CLI builds, `Project.build(...)`, desktop builds, and `compile.bash` all load the same project extensions, install `extensions/localisation/`, and resolve its hook through HeavenBase. Vanilla-reference discovery resolves `PIHC3_HOI4_GAME_ROOT` first, the shared `paradev.hoi4.game_root` desktop/config value second, and the existing platform default last. Artifact-emitting family, module, and collection selectors keep their requested non-localization compilation scope; PIHC3 expands only the localization publication closure so native and migrated baseline ownership stays deterministic across full, cached, and partial builds. The shared publication ledger removes only tracked predecessor paths and refuses to overwrite differing untracked legacy replacements.

The first process after an extension change validates and registers PIHC3's
HeavenBase modules. ParaDev then stores an automatically maintained,
Git-ignored receipt at `.paradev/cache/extension-install.json`. Later GUI, CLI,
and agent requests verify the extension bytes, descriptor keys, and durable
Registry fingerprints before reusing it. Users should not edit this file; it is
safe to delete, and ParaDev recreates it. Concurrent ParaDev processes share
one guarded registration path, so opening the desktop while a CLI query starts
does not produce a Registry compare-and-set error.

Large PIHC3 builds can spend time checking existing generated paths before writing. The CLI progress stream and desktop Build view report this honestly as **Validating publication** at 75%; it is a live safety phase, not a stalled build or a simulated estimate. Clean/full, cached, family-partial, and module-partial builds use the same phase.

Inspect the project:

```bash
rtk uv run paradev project projects/PIHC3 --json
rtk uv run paradev summary projects/PIHC3 --json
rtk uv run paradev build projects/PIHC3 --emit-manifests --json
```

Recommended PIHC3 source policy:

| Area | Policy |
| --- | --- |
| `src/` | ParaDev-native authored source. |
| `extensions/` | Project-owned HeavenBase Entity and compiler code; generated descriptors stay under each extension's `.paradev/` folder. |
| `scripts/` | Current validation and generated-state utilities only. |
| `scripts/review/` | Optional historical parity review utilities. |
| `docs/migration/` | One migration-complete cutover note; Git history retains the retired importer reports. |

The cutover note states that migration is complete. Historical evidence is
optional review input, never a PIHC3 compilation source or authoring workflow.

Each extension keeps its editable implementation at
`extensions/<family>/__init__.py`. Its generated HeavenBase Registry
descriptor is system-owned at
`extensions/<family>/.paradev/meta.yaml`; ordinary module authors do not edit
it. `scripts/hide_project_extension_metadata.py` audits this layout without
writing, while `--write` performs the resumable byte-preserving migration.
ParaDev stages an exact standard HeavenBase module artifact internally, so all
extensions still use HeavenBase 0.1.2.2 installation and resolution.
For a genuinely PIHC3-owned persistence type, the Python `hb.Entity` class is
the only Entity-schema source. Built-in HoI4 types reuse ParaDev's canonical
Entities and keep only a thin project compiler overlay. In both cases, the
registered family owns resource slots and compilation hooks; the hidden
path-target descriptor contains Registry identity and versioning rather than
an inline duplicate schema. This is verified for all 70 PIHC3 module-family
bundles through the real Registry path; `localisation` is the one auxiliary
writer/postprocessor bundle.
Completed family rename and consolidation history is not part of the live
Registry. PIHC3 descriptors, compiler classes, and family inspection contain
only current authoring and compilation contracts; use a clean build when
upgrading from a pre-cutover project tree.

For end-user authoring, use the family shorthand in `Project.create_module(...)`. PIHC3 currently has one project-local starter template for each scaffold-owned family, so `idea`, `idea_category`, `focus`, `trait`, `event`, `decision`, `modifier`, `opinion_modifier`, `wargoal`, `doctrine`, `faction`, `military_industrial_organization`, `scripted_gui`, `scripted_effect`, `scripted_trigger`, `on_action`, `character`, `country`, `state`, `state_lore`, `entity`, `resource`, `strategic_region`, `division`, `ideology`, `special_project`, `balance_of_power`, `intelligence_agency`, `game_rule`, `unit_medal`, `operative_codename`, `resistance_activity`, `continuous_focus`, `difficulty_setting`, `operation_token`, `operation_phase`, `operation`, `achievement`, `inventory_item`, `superevent`, `bookmark`, `autonomous_state`, `technology`, `building`, and `equipment` resolve to the PIHC3 templates. Full template ids remain available from `Project.templates()` when a family gains multiple variants.

The desktop module list also includes template-backed families that do not have existing source rows yet. That means the GUI can open an empty family such as `entity`, show its compact create form, and create the first module instance through the same SDK scaffold bridge.

When a family has multiple templates, the GUI shows a compact template dropdown in the create header. Families with a single template keep the one-click create path.

Graph creation also keeps the current selection as useful context. A new
Technology is a standalone `technology` module with `def.txt` and
preferred-language `main.loc`; no visible metadata is required. It can be
created without a selection using the safe `support_folder`/`pihc_all`
defaults, or it can inherit a selected technology's folder and column, start
two rows lower, and depend on that technology. The project provider excludes
the shared-source support module from the visual node graph without excluding
it from compilation. A new Doctrine starts two rows lower and joins the
selected path. In the MIO graph, **Add graph item** instead creates a child
trait inside the selected trait's existing organization, one row below it. The
provider-owned dialog reviews the domain fields and exact guarded plan before
Apply. Changing any field or a reviewed tree source invalidates that plan.

Open **Military & Research → Military Industrial Organizations**, then choose
**Open Military Industrial Organization trait tree** to inspect or edit MIOs.
The tree opens at project scope even when the source list has selected a
support module such as `ai_bonus_weights`; use the scope selector above the
canvas to switch organizations. The organization, trait graph, localization,
and image resources remain owned by their standalone MIO modules and the
project Registry provider.

Create a new PIHC3 idea:

```python
from paradev.sdk import Project

project = Project.load("projects/PIHC3")
plan = project.create_module(
    "idea",
    "IDEA_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Committee",
        "description": "A small project-local idea.",
        "language": "en",
        "cic": 0.02,
    },
)
if plan["blocked"]:
    raise RuntimeError(plan["diagnostics"])
```

This writes `def.txt` and `main.loc` under
`src/modules/idea/IDEA_TEST_FRIENDSHIP - Friendship Committee/`. The readable
folder suffix supplies the preferred-language title, so no redundant visible
`meta.yaml` is created. `cic: 0.02` writes
`industrial_capacity_factory = 0.02`; optional free-form `modifier` PDX can add
other modifiers.

Create several ideas through one reviewable transaction:

```python
requests = [
    {
        "family": "idea",
        "object_id": f"IDEA_BATCH_{name}",
        "values": {"title": f"Batch {name}", "cic": cic},
    }
    for name, cic in zip(("A", "B", "C", "D", "E"), (0.02, 0.05, 0.08, 0.12, 0.16), strict=True)
]
plan = project.create_modules(requests)
if plan["blocked"]:
    raise RuntimeError(plan)
applied = project.create_modules(requests, write=True, plan_hash=plan["plan_hash"])
```

`create_modules` plans by default. Apply requires the exact state-sensitive plan hash and has no force mode. ParaDev stages every requested file before committing any module; an existing, changed, or concurrently injected target blocks the batch instead of being overwritten.

The desktop AI chat now uses those same guarded transactions. Choose **Create content plan** and ask for one family of modules—for example, “Create ideas A, B, C, D, and E with CIC values 2%, 5%, 8%, 12%, and 16%”—or one collection, such as “Create a focus tree for C99 named Industrial Renewal.” The model receives PIHC3's live Registry-owned template kind, field labels, descriptions, defaults, choices, types, and existing-object references, including the Idea template's instruction that 2% is authored as `0.02`. The regular create dialog uses those same references to suggest existing Focus trees and Decision categories by readable name and stable id; the input remains editable for compatible external or newly planned ids. It uses the same GUI-ready form projection as the create dialogs, so all 391 current fields have readable labels and help text. Seventy-two domain-specific descriptions are declared by their owning extensions; ParaDev derives the other 319 from each field's real folder/file usage and marks the source transparently. Generated help never guesses family semantics and declared descriptions always win. The nine templates covering Ideas, Events, Decisions, Focuses/focus trees, Technologies, Characters, Countries, and Equipment now own descriptions for all 57 of their fields. Character gender and equipment yes/no controls use reviewed choices, while decision cost and equipment year use numeric validation. Extension-declared `advanced` flags control progressive disclosure even when a field has an empty default. The shared planner rechecks required values, choices, finite numbers, and booleans for every SDK, CLI, REST, MCP, desktop, and AI request before writing. ParaDev rejects a catalog whose form fields diverge from its template arguments, validates the structured response against those authoring-ready templates, and runs either one read-only `Project.create_modules(..., write=False)` module plan or `Project.scaffold_collection(..., write=False)` collection plan. Chat shows a review card and never writes files. Opening it prefills the existing batch or collection editor with the exact normalized request and dry-plan hash; any edit invalidates that hash, and only the editor's explicit apply action may create files. Project, template, source-root, duplicate-id, stale-state, and existing-draft checks fail closed instead of replacing user input.

The current authoring-capability gate covers all 51 visible PIHC3 families and
all 54 authoring templates. Every family has a module-create template and at least one
editable Registry slot; every localization-requiring template creates a
localization source; every visible copy/image slot has a safe module-relative
authoring destination; and every `loc` slot is explicitly typed for generic
GUI, SDK, MCP, and third-party clients. Focus, Technology, Doctrine, and MIO
also publish editable tree providers through the same Registry.

Shared Portrait creation is source-first as well. A new Portrait module starts
with `portraits/{object_id}.txt`, containing an empty male/female portrait-group
skeleton, and no metadata placeholder. Before Apply, dynamic template paths
are rendered in the draft tabs, so an object such as `PORTRAIT_CLOUD_GUARD`
shows a `PORTRAIT_CLOUD_GUARD` source instead of the implementation placeholder
`{object_id}`. Apply creates the source folder; the existing Image and Assets
surfaces then manage DDS and GFX resources through the Portrait Entity slots.

Existing `def.txt` files open through the same Registry-owned Guided editor.
Every safely editable scalar shows its full PDX-path context. The Idea, Event,
Decision, Focus, Technology, Character, Country, and Equipment extensions also
publish bilingual domain help directly from their Entity/family code; ParaDev
marks that help as declared and generates conservative path help for other
fields. Large event namespaces no longer lose Guided mode when they exceed the
bounded form size: the app shows the safe prefix plus an explicit “shown of
total” notice and a search box. Searching an event id such as
`C01_C02_GREENLIGHT.40` returns its complete safely editable section with
stable controls from the full source. Code mode remains available for omitted
values, blocks, lists, triggers, and effects. In the current PIHC3 tree all 42
event `def.txt` files have a Guided projection; 27 are deliberately partial
instead of silently falling back to Code-only.

Achievement, Division, Doctrine, Modifier, Inventory Item, State Lore, and
Superevent now use that same extension-owned contract for existing sources.
Their project-local Entity or Family declares the meaningful scalar fields and
the complete editable bodies for triggers, effects, regiment/support layouts,
doctrine rewards, modifier records, state-lore variants, and paired event options.
The desktop, SDK, CLI, REST, and MCP therefore receive the same labels, help,
exact source spans, and guarded updates; none of those clients contains a
family-name switch. Inventory Item now exposes one compact `item.json`
quantity-range field instead of hundreds of generated helper controls. Its
project-local extension expands that definition into the exact scripted
effects, scripted triggers, and helper localization during compilation.
State Lore similarly exposes only human lore localization and optional
conditional variants; its project-local compiler owns all selector and startup
registration boilerplate.

Script containers use the same extension contract for multiline bodies. All
8,279 Scripted Effects, 87 Scripted Triggers, 116 On Actions, and 111 Scripted
GUIs have a Guided projection owned by their project-local Entity/family code.
The form edits only the exact declared block interior, preserves its managed
braces and surrounding source, and reparses both the current path and final
PDX before Apply. Scripted GUI exposes its available `visible`, `triggers`,
`effects`, and `properties` blocks independently. Code mode remains available
for arbitrary source work.

Existing `.loc` tabs now use the same Registry-owned Guided/Code choice. The
form is enabled by the owning family's `loc` resource slot rather than a PIHC3
family list, and edits preserve localization keys, language/section headers,
surrounding source text, and LF/CRLF style. ParaDev rechecks the exact language, key,
duplicate occurrence, source span, and disk revision before Apply. Of the
current 5,159 localization files across 48 module families, all have a
valid Guided projection; 5,119 are complete and the largest 40 show the first
96 entries plus an explicit coverage notice, with Code mode available for the
remainder. This includes `equipment_module_category`, whose existing sources
were previously editable only as raw localization text.

Image and icon support is similarly resource-driven. When an Entity declares
a `copy` slot, its existing images and other opaque assets stay inside that
same semantic module and appear in the generic Image or Assets draft surface.
ParaDev resolves and validates the destination from the slot; users do not
create an `_asset_component` folder or maintain a parallel metadata record.

现有的 `def.txt` 文件也通过同一个 Registry 引导编辑器打开。每个可安全
编辑的标量都显示其 PDX 路径上下文。理念、事件、决议、国策、科技、角色、国家和装备
扩展还会直接从各自的 Entity/系列代码提供中英双语领域说明；其他字段使用保守的
路径说明。超出表单上限的大型事件命名空间不再完全退回代码模式：应用会显示可安全编辑的
部分、明确标出“已显示/总数”，并提供搜索框。搜索
`C01_C02_GREENLIGHT.40` 这类事件 ID 会返回它完整且可安全编辑的 section，控件身份
仍对应完整源文件。剩余值、区块、列表、触发器和效果仍可在代码模式中编辑。

成就、编制、教义、修正、库存物品、地区背景与超级事件也已经接入同一套由扩展
拥有的现有源文件契约。对应的项目本地 Entity 或 Family 会声明重要标量，以及
trigger、effect、团/支援编制、教义奖励、modifier record、地区背景变体和成对
event option 的完整可编辑区块。桌面端、SDK、CLI、REST 与 MCP 因而共用相同的
label、帮助、精确源区间与受保护更新，不需要按 family 名称分支。库存物品现在只需
编辑一个紧凑的 `item.json` 数量范围字段；项目本地扩展会在编译时生成完整的
scripted effects、scripted triggers 与 helper localization，不再把数百个生成项
暴露给作者维护。
地区背景也只暴露人工维护的 lore localization 与可选条件变体；selector、状态
routing 和启动注册全部由项目本地编译器生成。

现有 `.loc` 标签页也使用同一套 Registry 引导/代码模式。引导表单由 Entity 的
`loc` 资源槽启用，并保留键、语言/分节头、周边源文本和换行风格。当前 5,159 个
本地化文件均可生成引导表单；其中 5,119 个完整显示，最大的 40 个显示前 96 项和
明确的覆盖提示，其余内容继续使用代码模式。图片和图标则由同一 Entity 的 `copy`
资源槽进入通用图片/资产草稿，不再需要 `_asset_component` 或并行元数据。

For an existing idea, character, focus tree, technology, event, MIO source
module, or extension module, select it and use **Duplicate**. Enter only the
new folder/object id, review the projected paths, content hashes, file and byte
counts, then apply the exact plan. By default, the family's Registry-owned
identity-copy policy replaces complete old-id tokens in supported text and
paths while preserving binary images byte-for-byte. Durable hidden settings
in `.paradev/meta.yaml` follow the copy, so tree membership, subtype, and
other extension-owned semantics remain intact; transient import, evidence,
diagram, and transaction state stays behind. The copied module opens
immediately as an independent, consistently named module. SDK callers can
explicitly request `identity="preserve"` when a literal semantic clone is
genuinely intended.

Create a basic idea category shell:

```python
project.create_module(
    "idea_category",
    "IDEA_CATEGORY_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Era",
        "description": "A compact policy category shell.",
    },
)
```

The idea category template writes
`src/modules/idea_category/IDEA_CATEGORY_TEST_FRIENDSHIP - Friendship Era/`
and builds through PIHC3's project-local `idea_category` family to
`common/ideas/IDEA_CATEGORY_TEST_FRIENDSHIP.txt`. It follows the PIHC2
category-law shape with an `ideas = { IDEA_CATEGORY_* = { ... } }` wrapper,
defaulted `law = yes`, defaulted `use_list_view = yes`, and category plus
cost-factor localization keys. The law/list-view flags, cost-factor label, and
language are defaulted advanced fields, so the compact create form only needs
title and description.

Create a basic achievement shell:

```python
project.create_module(
    "achievement",
    "ACHIEVEMENT_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Achievement",
        "description": "A compact achievement shell.",
    },
)
```

The achievement template writes `src/modules/achievement/ACHIEVEMENT_TEST_FRIENDSHIP/` and builds through PIHC3's project-local `achievement` family to `common/achievements/ACHIEVEMENT_TEST_FRIENDSHIP.txt`. It follows the PIHC custom-achievement shape with `unique_id = pihc_3154495198`, localized `_NAME` and `_DESC` keys, the standard PIHC achievement eligibility gate, and an inert `happened = { always = no }` block. Unique id, localization keys, start-date gate, happened trigger, and language are defaulted advanced fields, so the compact create form only needs title and description. The migrated tree already has 49 canonical achievement modules: each owns its definition and localization, editor preview, and normal/grey/not-eligible DDS variants (147 compiled DDS files total). The former aggregate definition and separate support/asset component families are retired. Automatic DDS generation from a newly authored preview, achievement ribbon/UI authoring, and broader language review remain later slices; compiled DDS files are optional while authoring.

Create a basic inventory item helper shell:

```python
project.create_module(
    "inventory_item",
    "TEST_FRIENDSHIP",
    values={
        "title": "Friendship Keepsake",
        "description": "A compact inventory item shell.",
    },
)
```

The inventory item template writes `src/modules/inventory_item/TEST_FRIENDSHIP/` with one compact `item.json`, one human-authored `main.loc`, and an `icons/` resource folder. PIHC3's project-local `inventory_item` family expands the default quantity range into `common/scripted_effects/PIHC_INVENTORY_ITEM_TEST_FRIENDSHIP.txt`, the matching scripted triggers, and all deterministic count/tooltip localization while preserving the PIHC2 `ADD_INVENTORY_ITEM_*`, `DEL_INVENTORY_ITEM_*`, and `VAR_INVENTORY_ITEM_*` names. The compact create form only needs title and description; Advanced exposes the single helper-quantity expression when a nonstandard range is needed. Authors do not maintain generated helper PDX or localization. Inventory scan/debug aggregation, scripted GUI buttons, operation button wiring, icon generation, scripted-localisation hooks, and broader language review remain later slices.

Create a basic superevent shell:

```python
project.create_module(
    "superevent",
    "TEST_FRIENDSHIP",
    values={
        "title": "Friendship Crisis",
        "description": "A compact super event shell.",
    },
)
```

The superevent template writes `src/modules/superevent/TEST_FRIENDSHIP/` and builds through PIHC3's project-local `superevent` family to `events/SUPEREVENT_TEST_FRIENDSHIP.txt`. It uses the module object id as the event tag, creates a hidden `SUPER.TEST_FRIENDSHIP` country event, a paired `SUPER_NEWS.TEST_FRIENDSHIP` news event, and localization keys under `EVENT_SUPER_TEST_FRIENDSHIP`. Mark text, news title/description, news option text, music id, and language are defaulted advanced fields, so the compact create form only needs title and description. Full PIHC2 superevent import, aggregate `SUPER.txt`/`SUPER_NEWS.txt` emission, GUI/scripted-localisation assembly, event/news image DDS generation, music asset wiring, close-button behavior, and multi-language parity remain later slices.

Create a new PIHC3 country-leader trait the same way:

```python
project.create_module(
    "trait",
    "TRAIT_TEST_ARCHAEOLOGIST",
    values={
        "title": "Test Archaeologist",
        "description": "Slightly improves artifact discovery.",
    },
)
```

The trait template writes a canonical `src/modules/trait/TRAIT_TEST_ARCHAEOLOGIST - Test Archaeologist/` module containing only the editable definition and localization. The Registry-owned compiler defaults this template to the `country_leader` route, so ordinary trait folders need no `meta.yaml`; only scientist or unit-leader exceptions need an explicit route override.

Create a basic standalone country event with one option:

```python
project.create_module(
    "event",
    "EVENT_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Report",
        "description": "A compact event authored from the PIHC3 SDK.",
    },
)
```

The event template writes `src/modules/event/EVENT_TEST_FRIENDSHIP/` and defaults to a triggered `country_event` with `id = EVENT_TEST_FRIENDSHIP.1`. PIHC3 also has 41 imported PIHC2 event namespace modules such as `src/modules/event/C33_MAIN/`; those preserve compiled namespace PDX and consolidated English/Simplified Chinese localization. Event pictures, sprite files, `BCE`, `SUPER`, and `SUPER_NEWS` remain copy-overlay owned or future specialized slices.

Create a basic decision in the default PIHC3 decision category:

```python
project.create_module(
    "decision",
    "DECISION_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Outreach",
        "description": "A compact decision authored from the PIHC3 SDK.",
    },
)
```

The decision template writes `src/modules/decision/DECISION_TEST_FRIENDSHIP - Friendship Outreach/` and builds a `common/decisions/PIHC3_DECISIONS.txt` artifact. The outer category block in `def.txt` is the single source of truth for collection membership; the project-local Decision compiler overlay infers it during normalization, so the folder has no visible `meta.yaml`. Category id, icon, cost, and language are defaulted advanced fields, so the compact GUI create form only needs the object id plus title and description.

PIHC3 also has 458 imported PIHC2 decision modules under `src/modules/decision/` and 62 imported decision category collections under `src/collections/decision/`. All 458 authored definitions use the same metadata-free rule: exactly one category block is required and ambiguous multi-category modules fail with an actionable diagnostic. The two shared decision-support resource modules remain uncollected and also need no visible metadata. These records preserve compiled PIHC_dev category descriptors and decision PDX while normalizing localization into current ParaDev source slots. Icon/sprite generation and scripted GUI parity remain later slices.

Create a basic modifier:

```python
project.create_module(
    "modifier",
    "MODIFIER_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Momentum",
        "description": "A compact modifier authored from the PIHC3 SDK.",
    },
)
```

The modifier template writes `src/modules/modifier/MODIFIER_TEST_FRIENDSHIP/` and builds `common/modifiers/MODIFIER_TEST_FRIENDSHIP.txt`. The first modifier key defaults to `stability_factor = 0.05`; the modifier key and value are advanced fields for the compact GUI create form. The 109 migrated modifiers that must retain shared legacy output groups store that routing in system-owned `.paradev/meta.yaml`, so no visible metadata file is required.

Create a basic opinion modifier:

```python
project.create_module(
    "opinion_modifier",
    "OPINION_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Delegation",
        "description": "A compact diplomatic opinion modifier.",
    },
)
```

The opinion modifier template writes `src/modules/opinion_modifier/OPINION_TEST_FRIENDSHIP/` and builds `common/opinion_modifiers/OPINION_TEST_FRIENDSHIP.txt`. It follows the current local HOI4 `opinion_modifiers = { ... }` shape and defaults `value = 25` plus `decay = 1` as advanced fields. Trade modifiers, trust bounds, timers, balancing helpers, and PIHC2 opinion modifier import remain later slices.

Create a basic wargoal shell:

```python
project.create_module(
    "wargoal",
    "WARGOAL_TEST_FRIENDSHIP",
    values={
        "title": "Friendship War Goal",
        "description": "A compact war goal shell.",
    },
)
```

The wargoal template writes `src/modules/wargoal/WARGOAL_TEST_FRIENDSHIP/` and builds through PIHC3's project-local `wargoal` family to `common/wargoals/WARGOAL_TEST_FRIENDSHIP.txt`. It follows the current local HOI4 `common/wargoals/00_invasion.txt` shape with a `wargoal_types = { ... }` wrapper, one wargoal id, a localized war-name key, locked-off `allowed` trigger, empty `available` and `take_states` blocks, generation costs, state limits/costs, expiry, and threat. War-name key/text, allowed flag, costs, limits, expiry, threat, and language are defaulted advanced fields. Focus/event unlocks, peace-conference behavior, claim/core state presets, puppet/liberation variants, AI balancing, and PIHC2 wargoal import remain later slices.

Create basic scripted effect and scripted trigger shells:

```python
project.create_module(
    "scripted_effect",
    "EFFECT_TEST_FRIENDSHIP",
    values={"title": "Friendship Effect"},
)
project.create_module(
    "scripted_trigger",
    "TRIGGER_TEST_FRIENDSHIP",
    values={"title": "Friendship Trigger"},
)
```

The scripted effect template writes `src/modules/scripted_effect/EFFECT_TEST_FRIENDSHIP/` and builds `common/scripted_effects/EFFECT_TEST_FRIENDSHIP.txt`. The scripted trigger template writes `src/modules/scripted_trigger/TRIGGER_TEST_FRIENDSHIP/` and builds `common/scripted_triggers/TRIGGER_TEST_FRIENDSHIP.txt`. These starter templates expose `title` plus a multiline body field. The effect starts empty and the trigger starts with `always = yes`; authors can create useful source without opening raw Code mode or maintaining metadata. PIHC2 scripted effect/trigger import remains a later slice.

Create a basic on-action hook shell:

```python
project.create_module(
    "on_action",
    "ONACTION_TEST_FRIENDSHIP",
    values={"title": "Friendship Hook"},
)
```

The on-action template writes `src/modules/on_action/ONACTION_TEST_FRIENDSHIP/` and builds through PIHC3's project-local `on_action` family to `common/on_actions/ONACTION_TEST_FRIENDSHIP.txt`. It follows the current local HOI4 `common/on_actions/*.txt` shape with an `on_actions = { ... }` wrapper, defaults to the documented `on_monthly` hook, and emits an `effect = { }` block whose body is directly editable in the create form. The hook name is a defaulted advanced field. Event/random-event routing, scope-specific hook presets, DLC gating, and PIHC2 on-action import remain later slices.

Create a Focus node from the Focus-tree diagram:

1. Open **National Focuses**, select the owning tree, and choose **Add Focus**.
2. Enter the Focus id, title, description, position, and optional parent or prerequisite.
3. Review the new module or exact module-owned `def.txt` edit.
4. Apply only if the source revisions still match.

Each of the 28 trees is an ordered
`src/collections/focus/<TREE> - <title>/` collection. `def.txt` owns the tree
wrapper and country selection. Each Focus module keeps its authoritative tree
link in system-owned `.paradev/meta.yaml`; the template, Add Focus workflow,
copy transaction, and SDK maintain that hidden value, so authors do not edit a
one-line routing file. Each of the 738 nodes is a standalone
`src/modules/focus/<FOCUS_ID> - <preferred-language title>/` module containing
one `focus = { ... }` definition, its localization, `preview.png`, and its exact
compiled DDS/GFX resources. The Registry-backed PIHC3 Focus Entity recompiles
those modules inside the owning collection without a parallel `focus_tree` or
asset-component source.

Create a minimal Military Industrial Organization:

```python
project.create_module(
    "military_industrial_organization",
    "MIO_C01_FRIENDSHIP_ARSENAL",
    values={
        "title": "Friendship Arsenal",
        "description": "A C01 infantry-equipment organization.",
        "country_tag": "C01",
        "equipment_type": "infantry_equipment",
        "research_category": "infantry_weapons",
        "reliability": 0.05,
    },
)
```

The new titled folder is the single source of truth: it needs no visible
metadata, owns one game-shaped organization source under
`common/military_industrial_organization/organizations/`, and owns one compact
localization source under `localization/`. It starts with one initial trait and
one positioned trait, so it opens immediately in the MIO tree view. Imported
MIOs use the same family and folder contract; their importer evidence stays
hidden under `.paradev/`.

Create a basic character shell:

```python
project.create_module(
    "character",
    "CHARACTER_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Envoy",
        "description": "A basic PIHC3 character shell.",
    },
)
```

The character template writes `src/modules/character/CHARACTER_TEST_FRIENDSHIP/` and builds through PIHC3's project-local `character` family to `common/characters/CHARACTER_TEST_FRIENDSHIP.txt`. It creates a named character with a gender field and PIHC-style `_NAME`/`_DESC` localization. PIHC3 also has 250 imported PIHC2 character modules under `src/modules/character/`; those preserve compiled character PDX and English/Simplified Chinese localization. Portrait DDS generation, portrait sprite declarations, random-character portraits, animation strips, and role-specific authoring helpers remain later slices.

Create a basic country definition shell:

```python
project.create_module(
    "country",
    "COUNTRY_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Country",
        "description": "A compact country definition shell.",
    },
)
```

The country template writes `src/modules/country/COUNTRY_TEST_FRIENDSHIP/` and builds through PIHC3's project-local `country` family to `common/countries/COUNTRY_TEST_FRIENDSHIP.txt`. It creates the common country definition shell with graphical culture and `rgb` color fields refreshed from current local HOI4 country files, plus the required `COUNTRY_TEST_FRIENDSHIP` and uppercase `COUNTRY_TEST_FRIENDSHIP_DESC` localization keys. Country tag registration, history files, flags, portraits, map ownership, and PIHC2 country import remain later slices.

Create a basic state history shell:

```python
project.create_module(
    "state",
    "999",
    values={
        "title": "Friendship Province",
    },
)
```

The state template writes `src/modules/state/999 - Friendship Province/` and
builds through PIHC3's project-local `state` family to
`history/states/999.txt`. The numeric module id is the State id; it is not
repeated in metadata or a form field. `main.loc` owns `STATE_999`, and existing
State modules also keep each declared province's `VICTORY_POINTS_<province>`
name beside the definition. The State Entity aggregates those names into the
three game-facing language files, so editing or partially building one State
cannot publish a truncated localization file. Owner, manpower, category,
infrastructure, resources, and other scripted fields remain ordinary `def.txt`
authoring points. In **Guided**, every State exposes its province ids as one
integer per line and each `victory_points` block as one `province score` pair
per row. These controls come from the State Registry extension, preserve the
surrounding PDX exactly, and reject invalid or incomplete rows before Save.

Create a basic state-lore shell:

```python
project.create_module(
    "state_lore",
    "STATE_LORE_999",
    values={
        "title": "Friendship Harbor",
        "description": "A compact lore panel.",
    },
)
```

The state-lore template writes only `main.loc` under `src/modules/state_lore/STATE_LORE_999 - <title>/`; use the matching State module's preferred-language title. PIHC3's project-local `StateLore` Entity derives state `999` exclusively from the object id and generates the shared `common/scripted_localisation/PIHC_STATE_LORES.txt` and `common/on_actions/PIHC_STATE_LORES.txt` aggregates, plus `localisation/english/STATE_LORE_999_l_english.yml`. The hidden advanced State ID value is a creation-time numeric check and is never stored or used as a second source of truth.

Most lores need no other source. For conditional text, add an optional
`variants.pdx`; Guided mode exposes both fields:

```pdx
variant = {
    localization_key = STATE_LORE_999_0
    trigger = {
        has_global_flag = PIHC_GLOBAL_FLAG_EXAMPLE
    }
}
```

Add the referenced localization key to `main.loc` in every language that owns
the default `STATE_LORE_999` text. ParaDev rejects empty triggers, duplicate or
foreign localization keys, compiler-owned `check_variable` routing, and
missing translated variants before publication.

Create a basic model entity shell:

```python
project.create_module(
    "entity",
    "ENTITY_TEST_FRIENDSHIP",
    values={"title": "Friendship Model"},
)
```

The entity template creates `meta.yaml` plus three editable PDX files under `src/modules/entity/ENTITY_TEST_FRIENDSHIP/gfx/models/ENTITY_TEST_FRIENDSHIP/`: `mesh.gfx`, `entity.asset`, and `animations.asset`. It follows the PIHC2/HOI4DEV split with one `pdxmesh`, one `entity`, and one named animation declaration. Mesh path, mesh/entity names, texture placeholders, shader, scale, state, and animation are defaulted advanced fields, so the compact create form only needs a title.

In the desktop app, click **Apply** once to create those starter files. Source and asset editing deliberately stay locked before that first apply so unsaved edits cannot disappear during scaffolding. After the project refreshes, open **Assets** and add one exported `.mesh` plus one exported `.anim`; arbitrary incoming filenames are safely mapped to the full paths declared by `mesh_file` and `animation_file`. The animation path is derived from the advanced animation name, so the basic form does not ask for a second filename. Textures (`.dds`, `.png`, or `.tga`) may be added in the same tab. Use the exact row-level **Replace** action for an existing binary, especially when the legacy aggregate contains duplicate basenames. ParaDev refuses empty files, mismatched upload/target extensions, out-of-module or symlinked paths, implicit overwrites, case/Unicode-equivalent targets, ambiguous duplicate basenames, and selections whose files resolve to the same target. Pending assets are limited to 32 files and 64 MB in total; if two reads overlap for one target, the later selection wins. Editing pauses while **Apply** is in flight, and the backend anchors writes to no-follow directory handles so a concurrently swapped symlink cannot redirect bytes. Use the **Image** tab when PNG-to-DDS or PNG-to-TGA conversion is required.

The module may be scaffolded while incomplete, but its build is intentionally blocked until the exact referenced mesh exists in the mesh slot and the exact referenced animation exists in the animation slot. A texture or wrong-type binary at either configured path does not satisfy the check. ParaDev also verifies the Paradox `pdxasseti` v2 container structure, requires the basename-only `animations.asset` reference and animation binary to share a directory, checks the `mesh.gfx` file reference, and validates the mesh/entity/state/animation links; renamed text, header-only or truncated exports, misplaced animations, and internally inconsistent PDX definitions cannot report a successful build. Once both required binaries and definitions are valid, a targeted build emits the three PDX files plus those two binary assets. The default texture names remain placeholders; supply the textures required by the exported model before expecting it to render correctly in-game.

The migrated `HOI4DEV_ENTITIES` module is separate from that starter. Its checked-in source snapshot preserves the complete contracted PIHC2 inventory—312 files, 134 `info.json` mappings, six model roots, and the `entities.json` assignment table—and 182 byte-identical compiled inputs: 9 PDX model/entity files plus 173 mesh, animation, texture, and image assets. During a ParaDev build, the 173 static assets remain byte-identical while the 9 PDX files are parsed and canonically formatted without changing their ordered records, operators, scalar types, or values. Its strict portable importer can regenerate only the `compiled-entities`-owned aggregate; it does not overwrite template-created modules. Splitting the aggregate into 134 independently generated model records and exposing guided binary-asset replacement remain later authoring improvements, but PIHC2 entity migration itself is no longer future work.

Create a basic resource shell:

```python
project.create_module(
    "resource",
    "RESOURCE_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Resource",
        "description": "A compact strategic resource shell.",
    },
)
```

The resource template writes `src/modules/resource/RESOURCE_TEST_FRIENDSHIP/` and builds through PIHC3's project-local `resource` family to `common/resources/RESOURCE_TEST_FRIENDSHIP.txt`. It follows the current local HOI4 `common/resources/00_resources.txt` shape with a `resources = { ... }` wrapper, one resource id, an icon frame, civilian-industry trade value, convoy trade value, and local label/description keys. Icon frame, `cic`, `convoys`, and language are defaulted advanced fields. State resource placement, market and AI balancing, resource-strip art, define updates, and PIHC2 resource import remain later slices.

Create a basic land division history shell:

```python
project.create_module(
    "division",
    "DIVISION_TEST_FRIENDSHIP",
    values={"title": "Friendship Guard"},
)
```

The division template writes `src/modules/division/DIVISION_TEST_FRIENDSHIP/` and builds through PIHC3's project-local `division` family to `history/units/DIVISION_TEST_FRIENDSHIP.txt`. It follows the current local HOI4 `history/units` shape with one `division_template` and one deployed `units = { division = { ... } }` block. Template name, division name, starting location, regiment type, experience factor, and equipment factor are defaulted advanced fields, so the compact GUI create form only needs the object id plus title. PIHC2 division import, country OOB grouping, name-list wiring, support companies, air/naval units, starting stockpiles, and equipment production remain later slices.

Create a basic ideology group shell:

```python
project.create_module(
    "ideology",
    "IDEOLOGY_TEST_FRIENDSHIP",
    values={
        "title": "Friendship League",
        "description": "A compact ideology group shell.",
    },
)
```

The ideology template writes `src/modules/ideology/IDEOLOGY_TEST_FRIENDSHIP/` and builds through PIHC3's project-local `ideology` family to `common/ideologies/IDEOLOGY_TEST_FRIENDSHIP.txt`. It follows the current local HOI4 `ideologies = { ... }` shape with one ideology group, one subtype, a color, basic rules, and world-tension impact fields. Subtype id/title, color, rules, tension fields, and language are defaulted advanced fields. Party names, country ideology setup, icons, modifiers, AI behavior, faction names, and PIHC2 ideology import remain later slices.

Create a basic special project shell:

```python
project.create_module(
    "special_project",
    "SP_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Experiment",
        "description": "A compact special project shell.",
    },
)
```

The special project template writes `src/modules/special_project/SP_TEST_FRIENDSHIP/` and builds through PIHC3's project-local `special_project` family to `common/special_projects/projects/SP_TEST_FRIENDSHIP.txt`. It follows the current local HOI4 special-project project shape with specialization, project tags, AI weight, availability, breakthrough cost, prototype time, complexity, project output, and one generic prototype reward. Specializations, project-tag definitions, prototype reward definitions, icons, facilities, equipment unlocks, scripted effects, and PIHC2 special project import remain later slices.

Create a basic balance-of-power shell:

```python
project.create_module(
    "balance_of_power",
    "BOP_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Balance",
        "description": "A compact balance-of-power shell.",
    },
)
```

The balance-of-power template writes
`src/modules/balance_of_power/BOP_TEST_FRIENDSHIP - Friendship Balance/` and
builds through PIHC3's project-local `balance_of_power` family to
`common/bop/BOP_TEST_FRIENDSHIP.txt`. It follows the current local HOI4
`common/bop/*.txt` shape with an initial value, a neutral range, one left side,
and one right side. Side ids, range ids, icon identifiers, weekly modifier
keys, weekly values, and language are defaulted advanced fields. Assets are
optional: custom side DDS files can live under `gfx/interface/bop/` and their
sprite declaration under `interface/bop/` in the same module, with those final
paths preserved at build time. The 8 migrated PIHC3 balances already use this
single-folder, no-redundant-metadata structure. Decision-category wiring,
side-specific events/decisions, dynamic graphics, additional ranges, and
balancing helpers remain later slices.

Create a basic intelligence agency shell:

```python
project.create_module(
    "intelligence_agency",
    "INTEL_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Bureau",
        "description": "A compact intelligence agency shell.",
    },
)
```

The intelligence agency template writes `src/modules/intelligence_agency/INTEL_TEST_FRIENDSHIP/` and builds through PIHC3's project-local `intelligence_agency` family to `common/intelligence_agencies/INTEL_TEST_FRIENDSHIP.txt`. It follows the current local HOI4 `common/intelligence_agencies/*.txt` shape with one `intelligence_agency = { ... }` record, a picture, localized name key, default trigger, and available trigger. Picture, default trigger, available trigger, and language are defaulted advanced fields. Agency upgrades, country-focus creation effects, logo asset generation, multiple alternate names, and PIHC2 intelligence agency import remain later slices.

Create a basic game rule shell:

```python
project.create_module(
    "game_rule",
    "RULE_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Rule",
        "description": "A compact game rule shell.",
    },
)
```

The game rule template writes `src/modules/game_rule/RULE_TEST_FRIENDSHIP/` and builds through PIHC3's project-local `game_rule` family to `common/game_rules/RULE_TEST_FRIENDSHIP.txt`. It follows the current local HOI4 `common/game_rules/*.txt` shape with a rule name/description, group, icon, one default option, and one alternate option. Group, icon, option tokens, option labels, option descriptions, alternate achievement allowance, and language are defaulted advanced fields. AI behavior presets, country-specific rule packs, scripted effects that consume rule choices, icon asset generation, and PIHC2 game rule import remain later slices.

Create a basic unit medal shell:

```python
project.create_module(
    "unit_medal",
    "UNITMEDAL_TEST_FRIENDSHIP",
    values={"title": "Friendship Medal"},
)
```

The unit medal template writes `src/modules/unit_medal/UNITMEDAL_TEST_FRIENDSHIP/` and builds through PIHC3's project-local `unit_medal` family to `common/unit_medals/UNITMEDAL_TEST_FRIENDSHIP.txt`. It follows the current local HOI4 `unit_medals = { ... }` shape with a government availability trigger, frame, icon, shared cost variable, one unit modifier, and one divisional commander XP effect. Government, frame, icon, cost, modifier key/value, one-time XP, and language are defaulted advanced fields, so the compact create form only needs a title. Full PIHC2 medal-pack import, country-specific medal sets, icon atlas work, modifier balancing, award unlock effects, and custom scripted triggers remain later slices.

Create a basic operative codename theme:

```python
project.create_module(
    "operative_codename",
    "OPERATIVECODENAME_TEST_FRIENDSHIP",
    values={"title": "Friendship Operatives"},
)
```

The operative codename template writes `src/modules/operative_codename/OPERATIVECODENAME_TEST_FRIENDSHIP/` and builds through PIHC3's project-local `operative_codename` family to `common/units/codenames_operatives/OPERATIVECODENAME_TEST_FRIENDSHIP.txt`. It follows the current local HOI4 codename-theme shape with a localized theme name, target country list, `type = codename`, fallback name pattern, and two starter unique codenames. Countries, fallback pattern, starter codenames, and language are defaulted advanced fields, so the compact create form only needs a title. Full PIHC2 codename-pack import, multilingual codename lists, country coverage review, non-codename name-theme variants, and legacy parity review remain later slices.

Create a basic resistance activity shell:

```python
project.create_module(
    "resistance_activity",
    "RESISTANCEACTIVITY_TEST_FRIENDSHIP",
    values={"title": "Friendship Sabotage"},
)
```

The resistance activity template writes `src/modules/resistance_activity/RESISTANCEACTIVITY_TEST_FRIENDSHIP/` and builds through PIHC3's project-local `resistance_activity` family to `common/resistance_activity/RESISTANCEACTIVITY_TEST_FRIENDSHIP.txt`. It follows the current local HOI4 resistance activity shape with an availability trigger, weight block, maximum amount, duration, empty effect and state-modifier edit points, and a localized map alert text. Availability, weight, max amount, duration, and language are defaulted advanced fields, so the compact create form only needs a title. The default availability is `always = no`, keeping generated activities inert until an author wires the trigger and effects deliberately. Full PIHC2 resistance activity import, targeted sabotage variables, building-specific effects, occupation-law balancing, and legacy parity review remain later slices.

Create a basic continuous focus shell:

```python
project.create_module(
    "continuous_focus",
    "CONTFOCUS_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Effort",
        "description": "A compact continuous focus shell.",
    },
)
```

The continuous focus template writes `src/modules/continuous_focus/CONTFOCUS_TEST_FRIENDSHIP/` and builds through PIHC3's project-local `continuous_focus` family to `common/continuous_focus/CONTFOCUS_TEST_FRIENDSHIP.txt`. It follows the current local HOI4 `continuous_focus_palette = { ... }` shape with one palette, a country factor gate, position, one localized focus, default `enable`, empty modifier/select/cancel edit points, AI weight, strategy support, daily cost, and capitulation availability. Palette id, icon, availability, enable trigger, country/default/reset/position/AI/cost/capitulation fields, and language are defaulted advanced fields, so the compact create form only needs title and description. The default availability is `always = no`, keeping generated continuous focuses inert until an author wires unlock logic deliberately. Full PIHC2 continuous focus import, generic palette parity, country-specific unlocks, balancing, effects, AI strategy tuning, focus tree integration, and icon art remain later slices.

Create a basic difficulty setting shell:

```python
project.create_module(
    "difficulty_setting",
    "DIFFICULTY_TEST_FRIENDSHIP",
    values={"title": "Friendship Challenge"},
)
```

The difficulty setting template writes `src/modules/difficulty_setting/DIFFICULTY_TEST_FRIENDSHIP/` and builds through PIHC3's project-local `difficulty_setting` family to `common/difficulty_settings/DIFFICULTY_TEST_FRIENDSHIP.txt`. It follows the current local HOI4 `difficulty_settings = { difficulty_setting = { ... } }` shape with a setting key, AI modifier, target country list, and multiplier. Key, modifier, countries, and multiplier are defaulted advanced fields, so the compact create form only needs a title. Full PIHC2 difficulty pack import, per-country roster generation, custom modifier definitions, UI/localization review, balancing, and legacy parity review remain later slices.

Create a basic operation token shell:

```python
project.create_module(
    "operation_token",
    "OPTOKEN_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Asset",
        "description": "A compact operation token shell.",
    },
)
```

The operation token template writes `src/modules/operation_token/OPTOKEN_TEST_FRIENDSHIP/` and builds through PIHC3's project-local `operation_token` family to `common/operation_tokens/OPTOKEN_TEST_FRIENDSHIP.txt`. It follows the current local HOI4 operation-token shape with a token id, localized name and description keys, large icon, text icon, one intel source, and intel gain. Localization keys, icon, text icon, intel source, intel gain, and language are defaulted advanced fields, so the compact create form only needs title and description. Operation definitions, operation phases, token-awarding effects, targeted modifiers, multi-language parity, and PIHC2 operation-token import remain later slices.

Create a basic operation phase shell:

```python
project.create_module(
    "operation_phase",
    "OPPHASE_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Approach",
        "description": "A compact operation phase shell.",
    },
)
```

The operation phase template writes `src/modules/operation_phase/OPPHASE_TEST_FRIENDSHIP/` and builds through PIHC3's project-local `operation_phase` family to `common/operation_phases/OPPHASE_TEST_FRIENDSHIP.txt`. It follows the current local HOI4 operation-phase shape with a phase id, localized name, description and outcome keys, picture, icon, and an empty equipment edit point. Localization keys, outcome text, picture, icon, and language are defaulted advanced fields, so the compact create form only needs title and description. Operation definitions, phase requirements, return-on-complete behavior, equipment presets, map icons, outcome-extra text, and PIHC2 operation-phase import remain later slices.

Create a basic operation shell:

```python
project.create_module(
    "operation",
    "OPERATION_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Operation",
        "description": "A compact operation shell.",
    },
)
```

The operation template writes `src/modules/operation/OPERATION_TEST_FRIENDSHIP/` and builds through PIHC3's project-local `operation` family to `common/operations/OPERATION_TEST_FRIENDSHIP.txt`. It follows the current local HOI4 operation shape with operation icons, localized name/description keys, priority, duration, network strength, operative count, visible/available gates, empty requirements/equipment/outcome edit points, risk and cost fields, and three default phase-choice blocks. The default `available` trigger is `always = no`, keeping generated operations inert until an author wires the launch rules and outcome deliberately. Icons, priority, days, network strength, operative count, gates, risk/cost values, phase ids, phase weights, and language are defaulted advanced fields, so the compact create form only needs title and description. PIHC2 operation import, full operation roster parity, target selection, token awarding, equipment costs, AI weights, effects, map icon art, balancing, and multi-language parity remain later slices.

Create a basic bookmark shell:

```python
project.create_module(
    "bookmark",
    "BOOKMARK_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Scenario",
        "description": "A compact bookmark shell.",
    },
)
```

The bookmark template writes `src/modules/bookmark/BOOKMARK_TEST_FRIENDSHIP/` and builds through PIHC3's project-local `bookmark` family to `common/bookmarks/BOOKMARK_TEST_FRIENDSHIP.txt`. It follows the current local HOI4 `common/bookmarks/*.txt` shape with a `bookmarks = { bookmark = { ... } }` wrapper, localized name and description keys, date, picture, default country, one editable country setup block, a catch-all other-countries description block, and a final `randomize_weather` effect. Date, picture, default country, default flag, ideology, weather seed, country history text, other-countries history text, and language are defaulted advanced fields. Full bookmark rosters, portrait/leader setup, DLC gating, per-country ideas and focuses, map validation, and PIHC2 bookmark import remain later slices.

Create a basic autonomous state shell:

```python
project.create_module(
    "autonomous_state",
    "AUTONOMY_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Autonomy",
        "description": "A compact autonomous state shell.",
    },
)
```

The autonomous state template writes `src/modules/autonomous_state/AUTONOMY_TEST_FRIENDSHIP/` and builds through PIHC3's project-local `autonomous_state` family to `common/autonomous_states/AUTONOMY_TEST_FRIENDSHIP.txt`. It follows the current local HOI4 `common/autonomous_states/*.txt` shape with an `autonomy_state = { ... }` record, an id, freedom and manpower influence fields, rule/modifier blocks, subject and overlord AI desire blocks, an `allowed` trigger, and empty take/lose trigger shells. Default flag, puppet flag, freedom level, manpower influence, rule flags, autonomy manpower share, AI desire factors, garrison desire, allowed flag, and language are defaulted advanced fields. Autonomy-level chains, focus/event unlock logic, peace-conference weighting, country-specific restrictions, balancing helpers, and PIHC2 autonomous state import remain later slices.

Create a basic strategic region shell:

```python
project.create_module(
    "strategic_region",
    "331",
    values={
        "title": "Friendship Skies",
    },
)
```

The strategic region template writes
`src/modules/strategic_region/331 - Friendship Skies/` and builds through
PIHC3's project-local `strategic_region` family to
`map/strategicregions/331.txt`. The numeric folder id drives both the PDX id
and `STRATEGICREGION_331` localization key; it is not repeated in metadata.
The Region Entity aggregates every module's `main.loc` back into HoI4's three
`strategic_region_names` files. Province ids, temperature bounds, and weather
probabilities are defaulted advanced fields. Existing and newly scaffolded
province lists open in **Guided** as one integer per line through the same
Registry-declared exact-span editor used by States. Province-map validation,
naval terrain, static modifiers, and twelve-month weather profiles remain
later slices.

Create a basic technology shell:

```python
project.create_module(
    "technology",
    "TECHNOLOGY_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Research",
        "description": "A basic PIHC3 technology shell.",
    },
)
```

The technology template writes `src/modules/technology/TECHNOLOGY_TEST_FRIENDSHIP/` and builds through PIHC3's project-local `technology` family to `common/technologies/TECHNOLOGY_TEST_FRIENDSHIP.txt`. It creates a small `technologies = { ... }` block with folder position, category, research cost, start year, and AI weight; compiled assets are optional for a newly authored shell. The family has 300 independently editable technology nodes plus one readable `PIHC_TECHNOLOGY_SUPPORT - 共享技术支持` resource set in the same `src/modules/technology/` folder for the two shared game files. There is no separate support, component, or asset-component family. Generating DDS/GFX assets from `icon.png`, root technology GUI authoring, and equipment/doctrine coordination remain later work.

Existing MIO content lives in `src/modules/military_industrial_organization/`. Its seven concise folders keep AI bonus weights, organization definitions, policy definitions, and matching localization together while preserving the exact game-shaped `common/military_industrial_organization/**/*.txt` paths. Inspect organization trees through ParaDev's source-backed MIO view. Guided mode labels organization identity, trait tokens, tree positions and anchors, eligibility, equipment/research scope, and bonus blocks from the project-owned MIO Entity; Code mode remains available for the explicitly reported remainder of very large files. Do not maintain `game_id`, record inventories, tree summaries, or importer provenance. Folder suffixes supply their readable titles.

Create a basic grand doctrine shell:

```python
project.create_module(
    "doctrine",
    "DOCTRINE_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Doctrine",
        "description": "A compact grand doctrine shell.",
    },
)
```

The doctrine template writes `src/modules/doctrine/DOCTRINE_TEST_FRIENDSHIP/` and builds through PIHC3's project-local `doctrine` family to `common/doctrines/grand_doctrines/DOCTRINE_TEST_FRIENDSHIP.txt`. It follows the local post-1.17 HOI4 grand-doctrine shape with a folder, loc-backed name/description, icon, XP cost/type, `available` trigger, AI weight, one default track reference, one starter activation modifier, and an empty `milestones` block. Folder, icon, XP values, AI base weight, track, modifier key/value, and language are defaulted advanced fields. Doctrine folders, track definitions, subdoctrines, milestone rewards, UI balancing, and PIHC2 doctrine import remain later slices.

Create a basic faction template shell:

```python
project.create_module(
    "faction",
    "FACTION_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Faction",
        "description": "A compact faction template shell.",
    },
)
```

The faction template writes `src/modules/faction/FACTION_TEST_FRIENDSHIP/` and builds through PIHC3's project-local `faction` family to `common/factions/templates/FACTION_TEST_FRIENDSHIP.txt`. It follows the current local HOI4 faction-template shape with loc-backed name, manifest, icon, leader-join setting, `visible` and `available` triggers, one starter goal, and two default rules. Manifest, icon, leader-join flag, visibility, availability, starter goal, default rules, and language are defaulted advanced fields. Faction goals, manifests, rule groups, rules, upgrades, member upgrades, icon pools, AI initiative strategy, country creation effects, and PIHC2 faction import remain later slices.

Create a basic scripted GUI shell:

```python
project.create_module(
    "scripted_gui",
    "SCRIPTEDGUI_TEST_FRIENDSHIP",
    values={"title": "Friendship Scripted GUI"},
)
```

The scripted GUI template writes `src/modules/scripted_gui/SCRIPTEDGUI_TEST_FRIENDSHIP/` and builds through PIHC3's project-local `scripted_gui` family to `common/scripted_guis/SCRIPTEDGUI_TEST_FRIENDSHIP.txt`. It follows the current local HOI4 `scripted_gui = { ... }` shape with context type, window name, parent window token, a default-off `visible` trigger, and empty `effects`, `triggers`, and `properties` blocks. Context type, window name, parent window token, and visibility are defaulted advanced fields, so the compact create form only needs a title. Interface `.gui` layout files, decision-category wiring, dynamic lists, button effects, AI behavior, scripted localization, and PIHC2 scripted GUI import remain later slices.

Create a basic equipment shell:

```python
project.create_module(
    "equipment",
    "EQUIPMENT_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Kit",
        "description": "A compact infantry equipment shell.",
    },
)
```

The equipment template writes `src/modules/equipment/EQUIPMENT_TEST_FRIENDSHIP/` and builds through PIHC3's project-local `equipment` family to `common/units/equipment/EQUIPMENT_TEST_FRIENDSHIP.txt`. It creates a small `equipments = { ... }` block with current local HOI4-style fields such as `year`, `archetype`, `is_archetype`, `picture`, and `active` as defaulted advanced fields. PIHC2 equipment import, archetype-specific presets, modules, upgrades, and icon wiring remain later slices.

Create a basic building shell:

```python
project.create_module(
    "building",
    "BUILDING_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Hall",
        "description": "A compact custom building shell.",
    },
)
```

The building template writes
`src/modules/building/BUILDING_TEST_FRIENDSHIP - Friendship Hall/` and builds
through PIHC3's project-local `building` family to
`common/buildings/BUILDING_TEST_FRIENDSHIP.txt`. It creates a small
`buildings = { ... }` block with base cost, value, and infrastructure
construction effect as defaulted advanced fields.

## 中文

PIHC3 是用于迁移 PIHC Mod 系列的干净 ParaDev 项目。它已经有真实的项目 manifest、已提交的原生 source modules，以及用于 PIHC 专属编译规则的项目本地 Python families。旧的机器本地 `PIHC_dev` copy overlay 已移除；当前构建只使用已提交的 PIHC3 源文件树。

当前状态：

- 普通 Mod 作者应先从 `paradev new` 开始；
- 在 ParaDev 中选择当前 PIHC3 checkout 文件夹即可加载；
- 普通导航包含 51 个可见 semantic families，并全部提供项目本地创建 template；
- 当前契约包含 70 个 registered compiler families，另有 `localisation` postprocessor；2026-08-10 的 clean/cached 发布 smoke 记录了 14,574 个 active modules、106 个 collections、35,398 个 generated artifacts、0 diagnostics/errors，以及 `blocked: false`；
- 其余 20 个隐藏 module family 在语义整合继续进行时保留低层 HoI4 文件域；其中没有 `_asset_component`；
- 71 个项目 extension 文件夹全部是 HeavenBase 0.1.2.2 Registry modules；70 个 module types 都提供注册 compiler family，其中 63 个 PIHC3 自有类型还提供项目本地 concrete `hb.Entity` class，7 个 HoI4 内置类型使用精简 compiler overlay；`localisation` 是 postprocessor，不是 Entity；
- module object identity 来自 `src/modules/{family}/{object_id} - {首选语言标题}`；可读后缀给人看，object-id 前缀保持稳定；
- PIHC 专属行为不能放进 `src/paradev/`；
- 迁移代码应放在 PIHC3 项目目录的 `extensions/` HeavenBase 模块、脚本和 notes 中。

PIHC3 已经没有 `legacy/`、`_component`、`_asset_component` 或
`inactive_modules/`
源目录。图片、GFX、本地化和定义都放在拥有它们的 semantic module
内部。module 的可见 metadata 只在需要时使用 `inactive` 或 `comment`；folder
已经提供 title，真实的 collection membership 则位于隐藏的 `.paradev/`。
隐藏 provenance 可以保留，但不是编译源。
当前 live module 不再在 `.paradev/meta.yaml` 中重复任何编译设置。
trait 路由、doctrine subtype、equipment designer 归属、state id 与
portable Entity identity 都由项目 Registry 编译器根据 folder id 和 authored
source 推导。剩余隐藏 module manifest 只保存真实的 Focus Tree 或 Modifier
collection 归属。
Doctrine 现在只有一个 Registry family 和一个物理 source root：51 个当前
陆空 doctrine module 各自编译定义，`PIHC_DOCTRINE_SUPPORT - 教义共享支持`
保存共享 folder、track、海军文件与 doctrine reward 本地化。旧
`doctrine_definition` family 与 43 个不会编译的 1.17 以前节点已删除。

当前 family taxonomy：

| 分组 | 数量 | 用途 |
| --- | ---: | --- |
| Template-backed semantic families | 51 | GUI/CLI/SDK create flows，包括 inventory item、state lore、superevent 等 PIHC3 专属实体。 |
| 隐藏低层文件域 families | 20 | 保留必要的 HoI4 compatibility ownership，但不占据新手导航；它们是 concrete registered families，不是 asset sidecars。 |

Visibility 由每个 standalone Registry extension 声明，不来自
`paradev.yaml` 中央 family table，也不是 GUI 根据名称猜出来的。

在桌面编辑器中，**名称** 是首选语言的本地化标题，不是第二份
metadata。应用名称修改时，ParaDev 会先更新当前 Registry family
解析出的具体 title key，再把 module 文件夹同步为
`{object_id} - {可移植标题}`。ParaDev 不会为此创建只包含 title 的
`meta.yaml`；已有的 `collection`、`inactive` 和 `comment` metadata
保持不变。PIHC3 会把 Focus-tree membership 和旧 Modifier output grouping
之类的 compiler routing 放在隐藏的 `.paradev/meta.yaml`，由模板和图形操作
维护。普通用户可以通过**信息 → 合集**选择或清除 collection；该控件使用同一套
受 plan hash 保护的 SDK 原子事务，不需要打开隐藏文件。当前项目唯一可见的
module metadata 是 Bookmark 中有意保留的 `inactive: true`。

通过项目本地单行 wrapper 构建或 dry-plan PIHC3：

```bash
rtk uv run python projects/PIHC3/scripts/check_source_layout.py --json
rtk bash projects/PIHC3/compile.bash --json
rtk bash projects/PIHC3/compile.bash --clean --json
rtk bash projects/PIHC3/compile.bash --clean-only
rtk bash projects/PIHC3/compile.bash --summary --json
rtk bash projects/PIHC3/compile.bash --plan-only --json
rtk bash projects/PIHC3/compile.bash --family focus --summary --json
rtk bash projects/PIHC3/compile.bash --family focus --module FOCUS_C12_SHADOWS_OF_THE_PAST --summary --json
```

第一条命令会执行无写入、机器可读的 source-layout 审计。每次 wrapper 构建也会在 discovery 前静默运行同一检查，拒绝退役 component/legacy 目录、symlink alias、带“副本/copy”标记的路径、格式错误或重复的 `id - title` unit、空 unit、散落在 family 根目录的文件，以及用户可见的 system metadata。该 wrapper 只是便捷 surface，并不是另一套编译器。指定 `--family` 后，`--module` 可以直接使用项目浏览器显示的 object id，不必重复 `focus/` 前缀。直接 CLI 构建、`Project.build(...)`、桌面构建和 `compile.bash` 都会安装 `extensions/localisation/`，再通过 HeavenBase Registry 解析其 hook。Vanilla reference 会依次解析显式 `PIHC3_HOI4_GAME_ROOT`、共享的 `paradev.hoi4.game_root` 桌面/config 值，以及现有平台默认路径。带 artifact 写出的 family、module 和 collection selector 会保持所请求的非 localization 编译范围；PIHC3 只扩展 localization 发布闭包，使原生模块和迁移 baseline 的所有权在完整、缓存和局部构建之间保持确定一致。共享发布账本只清理已登记的前任路径；如果旧版流程留下的未登记 replacement 与计划内容不同，构建会拒绝覆盖。

extension 发生变化后的第一个进程会验证并注册 PIHC3 的 HeavenBase
模块。ParaDev 随后自动维护一个被 Git 忽略的
`.paradev/cache/extension-install.json` receipt。之后 GUI、CLI 和 agent
请求只有在 extension 字节、descriptor key 与持久 Registry fingerprint
全部匹配时才会复用它。用户不需要也不应编辑该文件；删除它是安全的，
ParaDev 会自动重建。多个 ParaDev 进程共用受保护的注册路径，因此在
CLI 查询启动时打开桌面端，不会再触发 Registry compare-and-set 错误。

大型 PIHC3 构建在写出前需要检查现有生成路径。CLI 进度流与桌面“构建”视图会在 75% 明确显示 **验证发布安全性**；这是仍在运行的数据安全阶段，不是程序卡死或模拟的耗时估算。清理/完整、缓存、family 局部和 module 局部构建都使用同一阶段。

检查项目：

```bash
rtk uv run paradev project projects/PIHC3 --json
rtk uv run paradev summary projects/PIHC3 --json
rtk uv run paradev build projects/PIHC3 --emit-manifests --json
```

建议的 PIHC3 源文件策略：

| 区域 | 策略 |
| --- | --- |
| `src/` | ParaDev 原生作者源文件。 |
| `extensions/` | PIHC3 自己拥有的 HeavenBase Entity 与编译器代码；生成的 descriptor 位于每个 extension 的 `.paradev/` 文件夹。 |
| `scripts/` | 仅保留当前 validation 与 generated-state utilities。 |
| `scripts/review/` | 可选的历史 parity review utilities。 |
| `docs/migration/` | 仅保留一份迁移完成说明；已退役导入器的历史记录由 Git 保留。 |

迁移完成说明明确当前切换已经结束。历史证据只能作为可选 review 输入，
不能成为 PIHC3 编译源或 authoring workflow。

每个 extension 的可编辑实现位于
`extensions/<family>/__init__.py`；生成的 HeavenBase Registry descriptor
由系统维护在 `extensions/<family>/.paradev/meta.yaml`，普通模块作者无需编辑。
`scripts/hide_project_extension_metadata.py` 默认只审计，添加 `--write` 后执行
可恢复、字节保持的迁移。ParaDev 会在内部暂存标准 HeavenBase module artifact，
所以所有 extension 仍然经过 HeavenBase 0.1.2.2 的统一安装与解析路径。
对于 PIHC3 自有 persistence type，Python `hb.Entity` class 是唯一的 Entity
schema 来源；HoI4 内置类型则复用 ParaDev canonical Entity，只保留项目级精简
compiler overlay。两种情况下都由注册 family 拥有 resource slots 和 compilation
hooks；隐藏 path-target descriptor 只保留 Registry identity/version，不复制
inline schema。真实 Registry gate 已覆盖全部 70 个 module-family bundle；
`localisation` 是唯一的辅助 writer/postprocessor bundle。

面向最终用户创建新模块时，优先在 `Project.create_module(...)` 中使用
family 简写。PIHC3 的 semantic families（包括 `idea`、`character`、
`focus`、`technology`、`decision`、`event`、`inventory_item`、
`state_lore`、`superevent` 等）都通过项目本地模板创建。Focus 节点是
独立 `focus` module，并通过 `collection` 归入对应 focus tree；可以在
图形编辑器中使用 **Add Focus**，也可以走同一 template/SDK 路径。

桌面端模块列表也会显示还没有现有源条目的 template-backed family。因此 GUI 可以打开类似 `entity` 这样的空 family，显示紧凑创建表单，并通过同一条 SDK scaffold bridge 创建第一个模块实例。

当某个 family 有多个模板时，GUI 会在创建表单头部显示一个紧凑的模板下拉框。只有一个模板的 family 仍然保持一键创建路径。

图形创建也会保留当前选择作为上下文。新 Technology 是独立的
`technology` module，只含 `def.txt` 与项目首选语言的 `main.loc`，不需要可见
metadata；未选择节点时可直接使用安全的 `support_folder`/`pihc_all` 默认值，
选择节点后则会继承其 folder 与列位置、向下两行，并依赖该 Technology。
项目 provider 会把共享源支持 module 留在编译范围内，但不会把它伪装成可视
节点。新 Doctrine 会向下两行并接入所选 path。在 MIO 图谱中，**添加图谱项目**
会改为在所选 trait 所属的现有 organization 内新建一个子 trait，并位于其下一行。
扩展驱动的对话框会在 Apply 前检查领域字段与精确受保护计划；修改任一字段或
被审阅的树源都会使计划失效。

创建新的 PIHC3 idea：

```python
from paradev.sdk import Project

project = Project.load("projects/PIHC3")
plan = project.create_module(
    "idea",
    "IDEA_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Committee",
        "description": "A small project-local idea.",
        "cic": 0.02,
    },
)
if plan["blocked"]:
    raise RuntimeError(plan["diagnostics"])
```

这会在
`src/modules/idea/IDEA_TEST_FRIENDSHIP - Friendship Committee/`
下写入 `def.txt` 和 `main.loc`。可读 folder suffix 已经提供 title，因此
不会再生成重复的可见 `meta.yaml` 或 legacy settings。`cic: 0.02`
会写出 `industrial_capacity_factory = 0.02`；也可用可选的
`modifier` PDX 文本添加其他 modifier。

通过一个可审阅事务创建多个 idea：

```python
requests = [
    {
        "family": "idea",
        "object_id": f"IDEA_BATCH_{name}",
        "values": {"title": f"Batch {name}", "cic": cic},
    }
    for name, cic in zip(("A", "B", "C", "D", "E"), (0.02, 0.05, 0.08, 0.12, 0.16), strict=True)
]
plan = project.create_modules(requests)
if plan["blocked"]:
    raise RuntimeError(plan)
applied = project.create_modules(requests, write=True, plan_hash=plan["plan_hash"])
```

`create_modules` 默认只生成计划。应用时必须传入与当前状态完全一致的 plan hash，并且没有 force 模式。ParaDev 会先暂存所有文件，再提交任何模块；已有、已变化或并发注入的目标会阻止整个批次，而不会被覆盖。

桌面端 AI 聊天现在也复用同一个事务。选择 **创建模块计划**，并要求创建同一个 family 的若干模块，例如“创建 idea A、B、C、D、E，CIC 分别为 2%、5%、8%、12%、16%”。模型会收到 PIHC3 当前 Registry 所声明的字段 label、description、default、choices、type 与现有对象引用，其中 Idea 模板会明确说明 2% 应写成 `0.02`。普通创建对话框也会使用同一引用契约，以可读名称和稳定 id 提示现有 Focus Tree 与 Decision Category；输入仍可编辑，以兼容外部或刚规划的新 id。它与创建对话框共用同一个 GUI-ready form projection，因此当前 391 个字段都有可读 label 与帮助文本。其中 72 条领域语义由所属 extension 显式声明；其余 319 条由 ParaDev 根据字段实际写入的目录或文件生成，并透明标注来源。生成的帮助不会猜测 family 语义，extension 声明始终优先。Idea、Event、Decision、Focus/Focus Tree、Technology、Character、Country 与 Equipment 的 9 个模板现在为全部 57 个字段自行声明说明。Character gender 和 Equipment 的 yes/no 控件使用已审查的 choices；Decision cost 与 Equipment year 使用数字校验。即使字段默认值为空，extension 明确声明的 `advanced` 现在也会控制渐进披露。共享 planner 会在写入前为每个 SDK、CLI、REST、MCP、桌面和 AI 请求重新检查必填值、choices、有限数字与布尔值。若 form fields 与 template arguments 不一致，ParaDev 会直接拒绝该 catalog；通过验证后也只运行一次只读的 `Project.create_modules(..., write=False)` 计划。聊天只显示 **审阅 5 个模块的计划** 卡片，绝不会写文件。打开卡片后，现有批量编辑器会得到精确的类型化请求与 dry-plan hash；修改任意字段都会使该 hash 失效，只有批量编辑器中明确点击 **应用** 才能创建文件。项目、模板、source root、重复 id、过期状态和已有草稿检查都会安全失败，不会覆盖用户输入。

当前 authoring-capability gate 覆盖全部 51 个可见 PIHC3 family 和 52 个项目
template。每个 family 都有创建模板与至少一个可编辑 Registry slot；需要
localization 的 template 都会创建 localization source；所有可见 copy/image
slot 都有安全的 module-relative authoring destination；每个 `loc` slot 也都
显式标注类型，供通用 GUI、SDK、MCP 和第三方 client 使用。Focus、
Technology、Doctrine 与 MIO 还通过同一 Registry 发布可编辑 tree provider。

对于已有的 idea、character、focus tree、technology、event、MIO source
module 或扩展模块，选中它并使用 **Duplicate**。只需输入新的目录/object
id，审阅预计路径、内容 hash、完整文件数和字节数，再应用完全一致的计划。
默认情况下，该 family 在 Registry 中声明的 identity-copy 策略会替换受支持
文本和路径中的完整旧 id token，同时逐字节保留二进制图片，并排除隐藏的
`.paradev/` 系统 metadata。复制后的内容会立即作为命名一致、彼此独立的新
模块打开。只有确实需要保留原有语义 id 的 SDK 调用者，才应显式传入
`identity="preserve"`。

创建一个基础 idea category shell：

```python
project.create_module(
    "idea_category",
    "IDEA_CATEGORY_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Era",
        "description": "A compact policy category shell.",
    },
)
```

idea category 模板会写入 `src/modules/idea_category/IDEA_CATEGORY_TEST_FRIENDSHIP/`，并通过 PIHC3 项目本地 `idea_category` family 构建到 `common/ideas/IDEA_CATEGORY_TEST_FRIENDSHIP.txt`。它遵循 PIHC2 category-law 形状，包含 `ideas = { IDEA_CATEGORY_* = { ... } }` wrapper、默认 `law = yes`、默认 `use_list_view = yes`，以及 category 和 cost-factor localization keys。law/list-view flags、cost-factor label 和 language 都是有默认值的 advanced 字段，所以紧凑创建表单只需要 title 和 description。完整 PIHC2 idea-category import、nested idea aggregation、legacy level ordering、icon parity 和 multi-language parity review 仍然留到后续切片。

创建一个基础 achievement shell：

```python
project.create_module(
    "achievement",
    "ACHIEVEMENT_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Achievement",
        "description": "A compact achievement shell.",
    },
)
```

achievement 模板会写入 `src/modules/achievement/ACHIEVEMENT_TEST_FRIENDSHIP/`，并通过 PIHC3 项目本地 `achievement` family 构建到 `common/achievements/ACHIEVEMENT_TEST_FRIENDSHIP.txt`。它遵循 PIHC custom-achievement 形状，包含 `unique_id = pihc_3154495198`、localized `_NAME` 和 `_DESC` keys、标准 PIHC achievement eligibility gate，以及默认不触发的 `happened = { always = no }` block。unique id、localization keys、start-date gate、happened trigger 和 language 都是有默认值的 advanced 字段，所以紧凑创建表单只需要 title 和 description。迁移后的树已经包含 49 个 canonical achievement modules；每个模块同时拥有 definition、localization、编辑器 preview，以及 normal/grey/not-eligible 三种 DDS（总计 147 个 compiled DDS files）。原来的 aggregate definition 和独立 support/asset component families 已退休。后续工作只剩从新建 preview 自动生成 DDS、achievement ribbon/UI authoring 和更广泛的语言审校；创作阶段允许暂时没有 compiled DDS。

创建一个基础 inventory item helper shell：

```python
project.create_module(
    "inventory_item",
    "TEST_FRIENDSHIP",
    values={
        "title": "Friendship Keepsake",
        "description": "A compact inventory item shell.",
    },
)
```

inventory item 模板会在 `src/modules/inventory_item/TEST_FRIENDSHIP/` 中创建一个紧凑的 `item.json`、一份只含人工文本的 `main.loc`，以及 `icons/` 资源目录。PIHC3 项目本地 `inventory_item` family 会把默认数量范围展开为 `common/scripted_effects/PIHC_INVENTORY_ITEM_TEST_FRIENDSHIP.txt`、对应 scripted triggers，以及确定性的 count/tooltip localization，并保留 PIHC2 的 `ADD_INVENTORY_ITEM_*`、`DEL_INVENTORY_ITEM_*`、`VAR_INVENTORY_ITEM_*` 命名。紧凑创建表单只需要 title 和 description；需要非标准数量时可在 Advanced 中编辑唯一的 helper-quantity 表达式。作者不再维护生成的 helper PDX 或本地化。Inventory scan/debug aggregation、scripted GUI buttons、operation button wiring、icon generation、scripted-localisation hooks 和更广泛的语言审校仍留到后续切片。

创建一个基础 superevent shell：

```python
project.create_module(
    "superevent",
    "TEST_FRIENDSHIP",
    values={
        "title": "Friendship Crisis",
        "description": "A compact super event shell.",
    },
)
```

superevent 模板会写入 `src/modules/superevent/TEST_FRIENDSHIP/`，并通过 PIHC3 项目本地 `superevent` family 构建到 `events/SUPEREVENT_TEST_FRIENDSHIP.txt`。它会把 module object id 作为 event tag，创建隐藏的 `SUPER.TEST_FRIENDSHIP` country event、配套的 `SUPER_NEWS.TEST_FRIENDSHIP` news event，以及 `EVENT_SUPER_TEST_FRIENDSHIP` 下的 localization keys。mark text、news title/description、news option text、music id 和 language 都是有默认值的 advanced 字段，所以紧凑创建表单只需要 title 和 description。完整 PIHC2 superevent import、聚合 `SUPER.txt`/`SUPER_NEWS.txt` emission、GUI/scripted-localisation assembly、event/news image DDS generation、music asset wiring、close-button behavior 和 multi-language parity 仍然留到后续切片。

用同样方式创建新的 PIHC3 country-leader trait：

```python
project.create_module(
    "trait",
    "TRAIT_TEST_ARCHAEOLOGIST",
    values={
        "title": "Test Archaeologist",
        "description": "Slightly improves artifact discovery.",
    },
)
```

trait 模板会写入规范的 `src/modules/trait/TRAIT_TEST_ARCHAEOLOGIST - Test Archaeologist/` 模块，其中只包含用户需要编辑的定义与本地化。Registry 所属的编译器会默认使用 `country_leader` 路由，所以普通 trait 文件夹不再需要 `meta.yaml`；只有 scientist 或 unit-leader 这类例外才需要显式覆盖路由。

创建一个只有一个选项的基础 standalone country event：

```python
project.create_module(
    "event",
    "EVENT_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Report",
        "description": "A compact event authored from the PIHC3 SDK.",
    },
)
```

event 模板会写入 `src/modules/event/EVENT_TEST_FRIENDSHIP/`，并默认生成 `id = EVENT_TEST_FRIENDSHIP.1` 的 triggered `country_event`。这个第一版 event 模板只用于新的手写模块；PIHC2 event import 和 namespace grouping 仍然留到后续迁移切片。

在默认 PIHC3 decision category 中创建一个基础 decision：

```python
project.create_module(
    "decision",
    "DECISION_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Outreach",
        "description": "A compact decision authored from the PIHC3 SDK.",
    },
)
```

decision 模板会写入 `src/modules/decision/DECISION_TEST_FRIENDSHIP - Friendship Outreach/`，并构建 `common/decisions/PIHC3_DECISIONS.txt` artifact。`def.txt` 最外层 category block 是 collection membership 的唯一真源；PIHC3 项目本地 Decision compiler overlay 会在 normalize 阶段自动推导，因此 module 文件夹不再需要可见的 `meta.yaml`。Category id、icon、cost 和 language 都是有默认值的 advanced 字段，所以紧凑 GUI 创建表单只需要 object id、title 和 description。现有 458 个 decision module 都使用同一规则：每个 `def.txt` 必须恰好声明一个 category，多个 category 会产生可操作的阻塞诊断；两个共享 support resource module 则保持无 collection、无可见 metadata。

创建一个基础 modifier：

```python
project.create_module(
    "modifier",
    "MODIFIER_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Momentum",
        "description": "A compact modifier authored from the PIHC3 SDK.",
    },
)
```

modifier 模板会写入 `src/modules/modifier/MODIFIER_TEST_FRIENDSHIP/`，并构建 `common/modifiers/MODIFIER_TEST_FRIENDSHIP.txt`。第一条 modifier key 默认是 `stability_factor = 0.05`；modifier key 和 value 都是 advanced 字段，紧凑 GUI 创建表单可以先隐藏它们。需要保留旧共享输出分组的 109 个已迁移 modifier 会把 routing 放在系统维护的 `.paradev/meta.yaml`，不再需要可见 metadata 文件。

创建一个基础 opinion modifier：

```python
project.create_module(
    "opinion_modifier",
    "OPINION_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Delegation",
        "description": "A compact diplomatic opinion modifier.",
    },
)
```

opinion modifier 模板会写入 `src/modules/opinion_modifier/OPINION_TEST_FRIENDSHIP/`，并构建 `common/opinion_modifiers/OPINION_TEST_FRIENDSHIP.txt`。它遵循当前本地 HOI4 `opinion_modifiers = { ... }` 形状，并默认把 advanced 字段设为 `value = 25` 和 `decay = 1`。trade modifiers、trust bounds、timers、balancing helpers，以及 PIHC2 opinion modifier import 仍然留到后续切片。

创建一个基础 wargoal shell：

```python
project.create_module(
    "wargoal",
    "WARGOAL_TEST_FRIENDSHIP",
    values={
        "title": "Friendship War Goal",
        "description": "A compact war goal shell.",
    },
)
```

wargoal 模板会写入 `src/modules/wargoal/WARGOAL_TEST_FRIENDSHIP/`，并通过 PIHC3 项目本地 `wargoal` family 构建到 `common/wargoals/WARGOAL_TEST_FRIENDSHIP.txt`。它遵循当前本地 HOI4 `common/wargoals/00_invasion.txt` 形状，生成一个 `wargoal_types = { ... }` wrapper、一个 wargoal id、localized war-name key、默认关闭的 `allowed` trigger、空 `available` 和 `take_states` blocks、generation costs、state limits/costs、expiry 和 threat。war-name key/text、allowed flag、costs、limits、expiry、threat 和 language 都是有默认值的 advanced 字段。focus/event unlocks、peace-conference behavior、claim/core state presets、puppet/liberation variants、AI balancing，以及 PIHC2 wargoal import 仍然留到后续切片。

创建基础 scripted effect 和 scripted trigger shell：

```python
project.create_module(
    "scripted_effect",
    "EFFECT_TEST_FRIENDSHIP",
    values={"title": "Friendship Effect"},
)
project.create_module(
    "scripted_trigger",
    "TRIGGER_TEST_FRIENDSHIP",
    values={"title": "Friendship Trigger"},
)
```

scripted effect 模板会写入 `src/modules/scripted_effect/EFFECT_TEST_FRIENDSHIP/`，并构建 `common/scripted_effects/EFFECT_TEST_FRIENDSHIP.txt`。scripted trigger 模板会写入 `src/modules/scripted_trigger/TRIGGER_TEST_FRIENDSHIP/`，并构建 `common/scripted_triggers/TRIGGER_TEST_FRIENDSHIP.txt`。这两个起步模板只把 `title` 暴露为主要创建字段；effect body 初始为空，trigger body 初始为 `always = yes`，PIHC2 scripted effect/trigger import 仍然留到后续切片。

创建一个基础 on-action hook shell：

```python
project.create_module(
    "on_action",
    "ONACTION_TEST_FRIENDSHIP",
    values={"title": "Friendship Hook"},
)
```

on-action 模板会写入 `src/modules/on_action/ONACTION_TEST_FRIENDSHIP/`，并通过 PIHC3 项目本地 `on_action` family 构建到 `common/on_actions/ONACTION_TEST_FRIENDSHIP.txt`。它遵循当前本地 HOI4 `common/on_actions/*.txt` 形状，生成一个 `on_actions = { ... }` wrapper，默认使用文档列出的 `on_monthly` hook，并生成一个可由作者继续填写或接到 scripted effect 的空 `effect = { }` block。hook name 是有默认值的 advanced 字段。event/random-event routing、scope-specific hook presets、DLC gating，以及 PIHC2 on-action import 仍然留到后续切片。

从 Focus-tree 图形编辑器创建新 Focus 节点：

1. 打开 **National Focuses**，选择所属树，然后点击 **Add Focus**。
2. 填写 Focus id、标题、描述、位置，以及可选的父节点或前置关系。
3. 审核新模块或对模块自有 `def.txt` 的精确修改。
4. 仅在源文件 revision 仍匹配时应用。

28 棵树现在是有序的
`src/collections/focus/<TREE> - <标题>/` collection：`def.txt` 保存树
wrapper 与国家选择条件。每个 Focus module 在系统维护的
`.paradev/meta.yaml` 中保存所属树；模板、Add Focus、复制事务和 SDK 会自动
维护这个隐藏值，作者无需编辑一行 routing 文件。738 个节点分别是独立的
`src/modules/focus/<FOCUS_ID> - <首选语言标题>/` 模块，各自拥有一个
`focus = { ... }` 定义、本地化、`preview.png`，以及完全一致的 DDS/GFX
资源。Registry 驱动的 PIHC3 Focus Entity 会把节点重新编译进所属
collection，不再需要平行的 `focus_tree` 或 asset-component 源目录。

创建一个最小 Military Industrial Organization：

```python
project.create_module(
    "military_industrial_organization",
    "MIO_C01_FRIENDSHIP_ARSENAL",
    values={
        "title": "Friendship Arsenal",
        "description": "A C01 infantry-equipment organization.",
        "country_tag": "C01",
        "equipment_type": "infantry_equipment",
        "research_category": "infantry_weapons",
        "reliability": 0.05,
    },
)
```

新目录就是唯一真源：只含标题的 `meta.yaml`、`common/military_industrial_organization/organizations/` 下一个游戏原生形状的 organization 源文件，以及 `localization/` 下一个紧凑本地化源文件。模板自带一个 initial trait 和一个有坐标的 trait，因此可以立即在 MIO 树视图中打开。导入的 MIO 也使用同一个 family 和目录契约；importer 证据只放在隐藏的 `.paradev/` 下。

创建一个基础 character shell：

```python
project.create_module(
    "character",
    "CHARACTER_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Envoy",
        "description": "A basic PIHC3 character shell.",
    },
)
```

character 模板会写入 `src/modules/character/CHARACTER_TEST_FRIENDSHIP/`，并通过 PIHC3 项目本地 `character` family 构建到 `common/characters/CHARACTER_TEST_FRIENDSHIP.txt`。它会创建一个带 `gender` 字段的命名角色，并写入 PIHC 风格的 `_NAME`/`_DESC` 本地化。`advisor`、`country_leader`、`corps_commander`、portraits，以及 PIHC2 character import 仍然留到后续切片。

创建一个基础 country definition shell：

```python
project.create_module(
    "country",
    "COUNTRY_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Country",
        "description": "A compact country definition shell.",
    },
)
```

country 模板会写入 `src/modules/country/COUNTRY_TEST_FRIENDSHIP/`，并通过 PIHC3 项目本地 `country` family 构建到 `common/countries/COUNTRY_TEST_FRIENDSHIP.txt`。它会创建 common country definition shell，包含从当前本地 HOI4 country 文件刷新过的 graphical culture 和 `rgb` color 字段，以及必需的 `COUNTRY_TEST_FRIENDSHIP` 和大写 `COUNTRY_TEST_FRIENDSHIP_DESC` 本地化键。country tag registration、history files、flags、portraits、map ownership，以及 PIHC2 country import 仍然留到后续切片。

创建一个基础 state history shell：

```python
project.create_module(
    "state",
    "999",
    values={
        "title": "Friendship Province",
    },
)
```

state 模板会写入 `src/modules/state/999 - Friendship Province/`，并通过 PIHC3 项目本地 `state` family 构建到 `history/states/999.txt`。数字目录 ID 同时就是 State ID，不需要在 metadata 或表单中重复维护。`main.loc` 负责 `STATE_999`，已有 State 还会把其胜利点省份的 `VICTORY_POINTS_<province>` 文本放在同一模块中。**Guided** 页面把省份列表显示为每行一个整数，并把每个 `victory_points` 区块显示为每行一组“省份 ID + 分值”；这些控件由 State Registry 扩展声明，会精确保留周边 PDX，并在保存前拒绝非法或不完整的行。owner、manpower、category、infrastructure、resources 及其他脚本字段仍可在同一 `def.txt` 中编辑。

创建一个基础 state-lore shell：

```python
project.create_module(
    "state_lore",
    "STATE_LORE_999",
    values={
        "title": "Friendship Harbor",
        "description": "A compact lore panel.",
    },
)
```

state-lore 模板只会在 `src/modules/state_lore/STATE_LORE_999 - <title>/` 中写入 `main.loc`；title 应使用对应 State 模块的首选语言名称。PIHC3 项目本地 `StateLore` Entity 只从 object id 推导 state `999`，并自动生成共享的 `common/scripted_localisation/PIHC_STATE_LORES.txt`、`common/on_actions/PIHC_STATE_LORES.txt` 与 `localisation/english/STATE_LORE_999_l_english.yml`。隐藏的 advanced State ID 仅用于创建时检查数字格式，不会保存，也不是第二份数据源。

大多数地区背景不需要其他文件。若需要条件文本，可增加一个可选
`variants.pdx`；Guided 模式会显示本地化键与 trigger：

```pdx
variant = {
    localization_key = STATE_LORE_999_0
    trigger = {
        has_global_flag = PIHC_GLOBAL_FLAG_EXAMPLE
    }
}
```

请在 `main.loc` 的每个默认文本语言中补齐该 key。ParaDev 会在发布前拒绝
空 trigger、重复或跨模块 key、由编译器负责的 `check_variable` routing，以及
缺失翻译的变体。

创建一个基础 model entity shell：

```python
project.create_module(
    "entity",
    "ENTITY_TEST_FRIENDSHIP",
    values={"title": "Friendship Model"},
)
```

entity 模板会创建 `meta.yaml`，并在 `src/modules/entity/ENTITY_TEST_FRIENDSHIP/gfx/models/ENTITY_TEST_FRIENDSHIP/` 下生成三个可编辑的 PDX 文件：`mesh.gfx`、`entity.asset` 和 `animations.asset`。它遵循 PIHC2/HOI4DEV 的拆分方式，生成一个 `pdxmesh`、一个 `entity` 和一个具名 animation 声明。mesh 路径、mesh/entity 名称、texture 占位符、shader、scale、state 和 animation 都是有默认值的 advanced 字段，所以紧凑创建表单只需要 title。

在桌面应用中，先点击一次 **应用** 来创建这些起始文件。第一次应用之前，源文件和资源编辑会保持锁定，防止脚手架创建时丢掉尚未写入的修改。项目刷新后，打开 **资源** 标签页，添加一个已导出的 `.mesh` 和一个已导出的 `.anim`；传入文件可以使用任意文件名，ParaDev 会安全映射到 `mesh_file` 和 `animation_file` 声明的完整路径。animation 路径由 advanced animation 名称推导，因此基础表单不会再询问第二个文件名。也可以在同一标签页添加 `.dds`、`.png` 或 `.tga` texture。替换现有二进制文件时请使用对应行的 **替换** 操作，尤其是 legacy aggregate 中存在同名文件时。ParaDev 会拒绝空文件、上传与目标扩展名不一致、模块外或经过 symlink 的路径、隐式覆盖、大小写或 Unicode 等价目标、无法消歧的同名文件，以及多个文件落到同一目标的选择。待写资源最多 32 个、合计 64 MB；同一目标的读取若发生重叠，以后选择的文件为准。**应用** 请求执行期间编辑区会暂停，后端写入会锚定到禁止跟随 symlink 的目录句柄，因此并发替换目录也无法把字节重定向到项目外。需要 PNG 转 DDS 或 TGA 时，请使用 **图片** 标签页。

条目可以在资源尚未齐全时先创建脚手架，但在 mesh slot 中存在精确引用的 mesh、并且在 animation slot 中存在精确引用的 animation 之前，构建会被明确阻止。即使 texture 或其他错误类型的二进制文件占用了声明路径，也不会通过校验。ParaDev 还会校验 Paradox `pdxasseti` v2 容器结构，要求 `animations.asset` 中只含文件名的引用与 animation 二进制文件位于同一目录，并校验 `mesh.gfx` 文件引用及 mesh/entity/state/animation 之间的链接；把文本改名、使用只有文件头或被截断的导出文件、把 animation 放错目录，或写出内部不一致的 PDX 定义，都不会得到成功构建。两个必需资源和定义都有效后，定向构建会输出三个 PDX 文件和这两个二进制资源。默认 texture 名称仍是占位符；若要让导出的模型在游戏中正确显示，还需提供模型实际引用的 texture。

已经迁移的 `HOI4DEV_ENTITIES` module 与这个 starter 相互独立。它的 checked-in source snapshot 保存了完整 contracted PIHC2 inventory：312 个文件、134 个 `info.json` mappings、6 个 model roots 和 `entities.json` assignment table，以及 182 个 byte-identical compiled inputs，包括 9 个 PDX model/entity 文件和 173 个 mesh、animation、texture、image assets。ParaDev 构建时会逐字节复制 173 个 static assets；9 个 PDX 文件会经过解析和 canonical formatting，但 ordered records、operators、scalar types 和 values 保持不变。严格的 portable importer 只会重新生成带 `compiled-entities` ownership 的 aggregate，不会覆盖通过模板新建的 modules。把 aggregate 拆成 134 个独立生成的 model records，以及为 binary asset replacement 提供更完整的向导，仍属于后续 authoring 改进；但 PIHC2 entity migration 本身已经不再是 future work。

创建一个基础 resource shell：

```python
project.create_module(
    "resource",
    "RESOURCE_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Resource",
        "description": "A compact strategic resource shell.",
    },
)
```

resource 模板会写入 `src/modules/resource/RESOURCE_TEST_FRIENDSHIP/`，并通过 PIHC3 项目本地 `resource` family 构建到 `common/resources/RESOURCE_TEST_FRIENDSHIP.txt`。它遵循当前本地 HOI4 `common/resources/00_resources.txt` 形状，生成一个 `resources = { ... }` wrapper、一个 resource id、icon frame、civilian-industry trade value、convoy trade value，以及本地 label/description keys。icon frame、`cic`、`convoys` 和 language 都是有默认值的 advanced 字段。state resource placement、market and AI balancing、resource-strip art、define updates，以及 PIHC2 resource import 仍然留到后续切片。

创建一个基础 land division history shell：

```python
project.create_module(
    "division",
    "DIVISION_TEST_FRIENDSHIP",
    values={"title": "Friendship Guard"},
)
```

division 模板会写入 `src/modules/division/DIVISION_TEST_FRIENDSHIP/`，并通过 PIHC3 项目本地 `division` family 构建到 `history/units/DIVISION_TEST_FRIENDSHIP.txt`。它遵循当前本地 HOI4 `history/units` 形状，生成一个 `division_template` 和一个 deployed `units = { division = { ... } }` block。template name、division name、starting location、regiment type、experience factor 和 equipment factor 都是有默认值的 advanced 字段，所以紧凑 GUI 创建表单只需要 object id 和 title。PIHC2 division import、country OOB grouping、name-list wiring、support companies、air/naval units、starting stockpiles 和 equipment production 仍然留到后续切片。

创建一个基础 ideology group shell：

```python
project.create_module(
    "ideology",
    "IDEOLOGY_TEST_FRIENDSHIP",
    values={
        "title": "Friendship League",
        "description": "A compact ideology group shell.",
    },
)
```

ideology 模板会写入 `src/modules/ideology/IDEOLOGY_TEST_FRIENDSHIP/`，并通过 PIHC3 项目本地 `ideology` family 构建到 `common/ideologies/IDEOLOGY_TEST_FRIENDSHIP.txt`。它遵循当前本地 HOI4 `ideologies = { ... }` 形状，生成一个 ideology group、一个 subtype、color、basic rules 和 world-tension impact 字段。subtype id/title、color、rules、tension fields 和 language 都是有默认值的 advanced 字段。party names、country ideology setup、icons、modifiers、AI behavior、faction names，以及 PIHC2 ideology import 仍然留到后续切片。

创建一个基础 special project shell：

```python
project.create_module(
    "special_project",
    "SP_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Experiment",
        "description": "A compact special project shell.",
    },
)
```

special project 模板会写入 `src/modules/special_project/SP_TEST_FRIENDSHIP/`，并通过 PIHC3 项目本地 `special_project` family 构建到 `common/special_projects/projects/SP_TEST_FRIENDSHIP.txt`。它遵循当前本地 HOI4 special-project project 形状，包含 specialization、project tags、AI weight、availability、breakthrough cost、prototype time、complexity、project output 和一个 generic prototype reward。specializations、project-tag definitions、prototype reward definitions、icons、facilities、equipment unlocks、scripted effects，以及 PIHC2 special project import 仍然留到后续切片。

创建一个基础 balance-of-power shell：

```python
project.create_module(
    "balance_of_power",
    "BOP_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Balance",
        "description": "A compact balance-of-power shell.",
    },
)
```

balance-of-power 模板会写入 `src/modules/balance_of_power/BOP_TEST_FRIENDSHIP/`，并通过 PIHC3 项目本地 `balance_of_power` family 构建到 `common/bop/BOP_TEST_FRIENDSHIP.txt`。它遵循当前本地 HOI4 `common/bop/*.txt` 形状，包含 initial value、一个 neutral range、一个 left side 和一个 right side。side ids、range ids、icon identifiers、weekly modifier keys、weekly values 和 language 都是有默认值的 advanced 字段。资产是可选的：自定义 side DDS 文件可以放在同一模块的 `gfx/interface/bop/` 下，对应 sprite declaration 放在 `interface/bop/` 下，构建时会保留这些最终路径。PIHC3 已迁移的 8 个 balance 都使用这种单文件夹结构和仅含 `title` 的 `meta.yaml`。decision-category wiring、side-specific events/decisions、dynamic graphics、additional ranges 和 balancing helpers 仍然留到后续切片。

创建一个基础 intelligence agency shell：

```python
project.create_module(
    "intelligence_agency",
    "INTEL_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Bureau",
        "description": "A compact intelligence agency shell.",
    },
)
```

intelligence agency 模板会写入 `src/modules/intelligence_agency/INTEL_TEST_FRIENDSHIP/`，并通过 PIHC3 项目本地 `intelligence_agency` family 构建到 `common/intelligence_agencies/INTEL_TEST_FRIENDSHIP.txt`。它遵循当前本地 HOI4 `common/intelligence_agencies/*.txt` 形状，生成一个 `intelligence_agency = { ... }` record，包含 picture、localized name key、default trigger 和 available trigger。picture、default trigger、available trigger 和 language 都是有默认值的 advanced 字段。agency upgrades、country-focus creation effects、logo asset generation、multiple alternate names，以及 PIHC2 intelligence agency import 仍然留到后续切片。

创建一个基础 game rule shell：

```python
project.create_module(
    "game_rule",
    "RULE_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Rule",
        "description": "A compact game rule shell.",
    },
)
```

game rule 模板会写入 `src/modules/game_rule/RULE_TEST_FRIENDSHIP/`，并通过 PIHC3 项目本地 `game_rule` family 构建到 `common/game_rules/RULE_TEST_FRIENDSHIP.txt`。它遵循当前本地 HOI4 `common/game_rules/*.txt` 形状，包含 rule name/description、group、icon、一个 default option 和一个 alternate option。group、icon、option tokens、option labels、option descriptions、alternate achievement allowance 和 language 都是有默认值的 advanced 字段。AI behavior presets、country-specific rule packs、消费 rule choices 的 scripted effects、icon asset generation，以及 PIHC2 game rule import 仍然留到后续切片。

创建一个基础 unit medal shell：

```python
project.create_module(
    "unit_medal",
    "UNITMEDAL_TEST_FRIENDSHIP",
    values={"title": "Friendship Medal"},
)
```

unit medal 模板会写入 `src/modules/unit_medal/UNITMEDAL_TEST_FRIENDSHIP/`，并通过 PIHC3 项目本地 `unit_medal` family 构建到 `common/unit_medals/UNITMEDAL_TEST_FRIENDSHIP.txt`。它遵循当前本地 HOI4 `unit_medals = { ... }` 形状，包含 government availability trigger、frame、icon、shared cost variable、一个 unit modifier，以及一个 divisional commander XP effect。government、frame、icon、cost、modifier key/value、one-time XP 和 language 都是有默认值的 advanced 字段，所以紧凑创建表单只需要 title。完整 PIHC2 medal-pack import、country-specific medal sets、icon atlas work、modifier balancing、award unlock effects 和 custom scripted triggers 仍然留到后续切片。

创建一个基础 operative codename theme：

```python
project.create_module(
    "operative_codename",
    "OPERATIVECODENAME_TEST_FRIENDSHIP",
    values={"title": "Friendship Operatives"},
)
```

operative codename 模板会写入 `src/modules/operative_codename/OPERATIVECODENAME_TEST_FRIENDSHIP/`，并通过 PIHC3 项目本地 `operative_codename` family 构建到 `common/units/codenames_operatives/OPERATIVECODENAME_TEST_FRIENDSHIP.txt`。它遵循当前本地 HOI4 codename-theme 形状，包含 localized theme name、target country list、`type = codename`、fallback name pattern，以及两个 starter unique codenames。countries、fallback pattern、starter codenames 和 language 都是有默认值的 advanced 字段，所以紧凑创建表单只需要 title。完整 PIHC2 codename-pack import、multilingual codename lists、country coverage review、non-codename name-theme variants，以及 legacy parity review 仍然留到后续切片。

创建一个基础 resistance activity shell：

```python
project.create_module(
    "resistance_activity",
    "RESISTANCEACTIVITY_TEST_FRIENDSHIP",
    values={"title": "Friendship Sabotage"},
)
```

resistance activity 模板会写入 `src/modules/resistance_activity/RESISTANCEACTIVITY_TEST_FRIENDSHIP/`，并通过 PIHC3 项目本地 `resistance_activity` family 构建到 `common/resistance_activity/RESISTANCEACTIVITY_TEST_FRIENDSHIP.txt`。它遵循当前本地 HOI4 resistance activity 形状，包含 availability trigger、weight block、maximum amount、duration、空的 effect 和 state-modifier edit points，以及 localized map alert text。availability、weight、max amount、duration 和 language 都是有默认值的 advanced 字段，所以紧凑创建表单只需要 title。默认 availability 是 `always = no`，避免生成的 activity 在作者明确接线 trigger 和 effects 前生效。完整 PIHC2 resistance activity import、targeted sabotage variables、building-specific effects、occupation-law balancing，以及 legacy parity review 仍然留到后续切片。

创建一个基础 continuous focus shell：

```python
project.create_module(
    "continuous_focus",
    "CONTFOCUS_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Effort",
        "description": "A compact continuous focus shell.",
    },
)
```

continuous focus 模板会写入 `src/modules/continuous_focus/CONTFOCUS_TEST_FRIENDSHIP/`，并通过 PIHC3 项目本地 `continuous_focus` family 构建到 `common/continuous_focus/CONTFOCUS_TEST_FRIENDSHIP.txt`。它遵循当前本地 HOI4 `continuous_focus_palette = { ... }` 形状，包含一个 palette、country factor gate、position、一个带本地化的 focus、默认 `enable`、空的 modifier/select/cancel edit points、AI weight、strategy support、daily cost 和 capitulation availability。palette id、icon、availability、enable trigger、country/default/reset/position/AI/cost/capitulation 字段和 language 都是有默认值的 advanced 字段，所以紧凑创建表单只需要 title 和 description。默认 availability 是 `always = no`，避免生成的 continuous focus 在作者明确接线 unlock 逻辑前生效。完整 PIHC2 continuous focus import、generic palette parity、country-specific unlocks、balancing、effects、AI strategy tuning、focus tree integration 和 icon art 仍然留到后续切片。

创建一个基础 difficulty setting shell：

```python
project.create_module(
    "difficulty_setting",
    "DIFFICULTY_TEST_FRIENDSHIP",
    values={"title": "Friendship Challenge"},
)
```

difficulty setting 模板会写入 `src/modules/difficulty_setting/DIFFICULTY_TEST_FRIENDSHIP/`，并通过 PIHC3 项目本地 `difficulty_setting` family 构建到 `common/difficulty_settings/DIFFICULTY_TEST_FRIENDSHIP.txt`。它遵循当前本地 HOI4 `difficulty_settings = { difficulty_setting = { ... } }` 形状，包含 setting key、AI modifier、target country list 和 multiplier。key、modifier、countries 和 multiplier 都是有默认值的 advanced 字段，所以紧凑创建表单只需要 title。完整 PIHC2 difficulty pack import、per-country roster generation、custom modifier definitions、UI/localization review、balancing 和 legacy parity review 仍然留到后续切片。

创建一个基础 operation token shell：

```python
project.create_module(
    "operation_token",
    "OPTOKEN_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Asset",
        "description": "A compact operation token shell.",
    },
)
```

operation token 模板会写入 `src/modules/operation_token/OPTOKEN_TEST_FRIENDSHIP/`，并通过 PIHC3 项目本地 `operation_token` family 构建到 `common/operation_tokens/OPTOKEN_TEST_FRIENDSHIP.txt`。它遵循当前本地 HOI4 operation-token 形状，包含 token id、localized name 和 description keys、large icon、text icon、一个 intel source 和 intel gain。localization keys、icon、text icon、intel source、intel gain 和 language 都是有默认值的 advanced 字段，所以紧凑创建表单只需要 title 和 description。Operation definitions、operation phases、token-awarding effects、targeted modifiers、multi-language parity 和 PIHC2 operation-token import 仍然留到后续切片。

创建一个基础 operation phase shell：

```python
project.create_module(
    "operation_phase",
    "OPPHASE_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Approach",
        "description": "A compact operation phase shell.",
    },
)
```

operation phase 模板会写入 `src/modules/operation_phase/OPPHASE_TEST_FRIENDSHIP/`，并通过 PIHC3 项目本地 `operation_phase` family 构建到 `common/operation_phases/OPPHASE_TEST_FRIENDSHIP.txt`。它遵循当前本地 HOI4 operation-phase 形状，包含 phase id、localized name、description 和 outcome keys、picture、icon，以及空的 equipment edit point。localization keys、outcome text、picture、icon 和 language 都是有默认值的 advanced 字段，所以紧凑创建表单只需要 title 和 description。Operation definitions、phase requirements、return-on-complete behavior、equipment presets、map icons、outcome-extra text 和 PIHC2 operation-phase import 仍然留到后续切片。

创建一个基础 operation shell：

```python
project.create_module(
    "operation",
    "OPERATION_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Operation",
        "description": "A compact operation shell.",
    },
)
```

operation 模板会写入 `src/modules/operation/OPERATION_TEST_FRIENDSHIP/`，并通过 PIHC3 项目本地 `operation` family 构建到 `common/operations/OPERATION_TEST_FRIENDSHIP.txt`。它遵循当前本地 HOI4 operation 形状，包含 operation icons、localized name/description keys、priority、duration、network strength、operative count、visible/available gates、空的 requirements/equipment/outcome edit points、risk/cost 字段，以及三个默认 phase-choice blocks。默认 `available` trigger 是 `always = no`，避免生成的 operation 在作者明确接线 launch rules 和 outcome 前生效。icons、priority、days、network strength、operative count、gates、risk/cost values、phase ids、phase weights 和 language 都是有默认值的 advanced 字段，所以紧凑创建表单只需要 title 和 description。PIHC2 operation import、完整 operation roster parity、target selection、token awarding、equipment costs、AI weights、effects、map icon art、balancing 和 multi-language parity 仍然留到后续切片。

创建一个基础 bookmark shell：

```python
project.create_module(
    "bookmark",
    "BOOKMARK_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Scenario",
        "description": "A compact bookmark shell.",
    },
)
```

bookmark 模板会写入 `src/modules/bookmark/BOOKMARK_TEST_FRIENDSHIP/`，并通过 PIHC3 项目本地 `bookmark` family 构建到 `common/bookmarks/BOOKMARK_TEST_FRIENDSHIP.txt`。它遵循当前本地 HOI4 `common/bookmarks/*.txt` 形状，生成一个 `bookmarks = { bookmark = { ... } }` wrapper，包含 localized name/description keys、date、picture、default country、一个可编辑 country setup block、一个 other-countries description block，以及末尾的 `randomize_weather` effect。date、picture、default country、default flag、ideology、weather seed、country history text、other-countries history text 和 language 都是有默认值的 advanced 字段。完整 bookmark roster、portrait/leader setup、DLC gating、per-country ideas/focuses、map validation，以及 PIHC2 bookmark import 仍然留到后续切片。

创建一个基础 autonomous state shell：

```python
project.create_module(
    "autonomous_state",
    "AUTONOMY_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Autonomy",
        "description": "A compact autonomous state shell.",
    },
)
```

autonomous state 模板会写入 `src/modules/autonomous_state/AUTONOMY_TEST_FRIENDSHIP/`，并通过 PIHC3 项目本地 `autonomous_state` family 构建到 `common/autonomous_states/AUTONOMY_TEST_FRIENDSHIP.txt`。它遵循当前本地 HOI4 `common/autonomous_states/*.txt` 形状，生成一个 `autonomy_state = { ... }` record，包含 id、freedom 和 manpower influence 字段、rule/modifier blocks、subject 和 overlord AI desire blocks、`allowed` trigger，以及空的 take/lose trigger shells。default flag、puppet flag、freedom level、manpower influence、rule flags、autonomy manpower share、AI desire factors、garrison desire、allowed flag 和 language 都是有默认值的 advanced 字段。autonomy-level chains、focus/event unlock logic、peace-conference weighting、country-specific restrictions、balancing helpers，以及 PIHC2 autonomous state import 仍然留到后续切片。

创建一个基础 strategic region shell：

```python
project.create_module(
    "strategic_region",
    "331",
    values={
        "title": "Friendship Skies",
    },
)
```

strategic region 模板会写入 `src/modules/strategic_region/331 - Friendship Skies/`，并通过 PIHC3 项目本地 `strategic_region` family 构建到 `map/strategicregions/331.txt`。数字目录 ID 同时驱动 PDX ID 与 `STRATEGICREGION_331` 本地化键，不需要在 metadata 中重复维护。Region Entity 会把各模块的 `main.loc` 聚合为 HOI4 所需的三个 `strategic_region_names` 文件。**Guided** 页面通过同一套 Registry 声明式精确区间编辑器，把省份列表显示为每行一个整数。province-map validation、naval terrain、static modifiers 和十二个月的 weather profiles 仍属于后续工作。

创建一个基础 technology shell：

```python
project.create_module(
    "technology",
    "TECHNOLOGY_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Research",
        "description": "A basic PIHC3 technology shell.",
    },
)
```

technology 模板会写入 `src/modules/technology/TECHNOLOGY_TEST_FRIENDSHIP/`，并通过 PIHC3 项目本地 `technology` family 构建到 `common/technologies/TECHNOLOGY_TEST_FRIENDSHIP.txt`。它会创建一个小型 `technologies = { ... }` block，包含 folder position、category、research cost、start year 和 AI weight；新建模块可以暂时不带 compiled assets。该 family 包含 300 个直观、可读且可独立编辑的 technology 节点，并在同一个 `src/modules/technology/` 下用 `PIHC_TECHNOLOGY_SUPPORT - 共享技术支持` 资源集保存两个共享游戏文件，不再存在独立的 support、component 或 asset-component family。由 `icon.png` 生成 DDS/GFX、root technology GUI authoring，以及 equipment/doctrine coordination 仍留到后续工作。

现有 MIO 内容位于 `src/modules/military_industrial_organization/`。七个简洁目录共同保存 AI bonus weights、organization definitions、policy definitions 和对应 localization，同时原样保留 `common/military_industrial_organization/**/*.txt` 游戏路径。用户可通过 ParaDev 的 source-backed MIO view 检查 organization trees。引导模式会从项目自有的 MIO Entity 读取军工机构标识、特质标识、树坐标与锚点、可用条件、装备/研究范围及加成块说明；对于非常大的文件，界面会明确报告未覆盖部分并保留代码模式。无需在 metadata 中维护 `game_id`、record inventories、tree summaries 或导入 provenance。目录后缀直接提供可读标题。

创建一个基础 grand doctrine shell：

```python
project.create_module(
    "doctrine",
    "DOCTRINE_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Doctrine",
        "description": "A compact grand doctrine shell.",
    },
)
```

doctrine 模板会写入 `src/modules/doctrine/DOCTRINE_TEST_FRIENDSHIP/`，并通过 PIHC3 项目本地 `doctrine` family 构建到 `common/doctrines/grand_doctrines/DOCTRINE_TEST_FRIENDSHIP.txt`。它遵循本地 post-1.17 HOI4 grand-doctrine 形状，包含 folder、由 loc 支持的 name/description、icon、XP cost/type、`available` trigger、AI weight、一个默认 track reference、一个起步 activation modifier，以及空的 `milestones` block。folder、icon、XP values、AI base weight、track、modifier key/value 和 language 都是有默认值的 advanced 字段。doctrine folders、track definitions、subdoctrines、milestone rewards、UI balancing，以及 PIHC2 doctrine import 仍然留到后续切片。

创建一个基础 faction template shell：

```python
project.create_module(
    "faction",
    "FACTION_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Faction",
        "description": "A compact faction template shell.",
    },
)
```

faction 模板会写入 `src/modules/faction/FACTION_TEST_FRIENDSHIP/`，并通过 PIHC3 项目本地 `faction` family 构建到 `common/factions/templates/FACTION_TEST_FRIENDSHIP.txt`。它遵循当前本地 HOI4 faction-template 形状，包含由 loc 支持的 name、manifest、icon、leader-join setting、`visible` 和 `available` triggers、一个 starter goal，以及两个 default rules。manifest、icon、leader-join flag、visibility、availability、starter goal、default rules 和 language 都是有默认值的 advanced 字段。faction goals、manifests、rule groups、rules、upgrades、member upgrades、icon pools、AI initiative strategy、country creation effects，以及 PIHC2 faction import 仍然留到后续切片。

创建一个基础 scripted GUI shell：

```python
project.create_module(
    "scripted_gui",
    "SCRIPTEDGUI_TEST_FRIENDSHIP",
    values={"title": "Friendship Scripted GUI"},
)
```

scripted GUI 模板会写入 `src/modules/scripted_gui/SCRIPTEDGUI_TEST_FRIENDSHIP/`，并通过 PIHC3 项目本地 `scripted_gui` family 构建到 `common/scripted_guis/SCRIPTEDGUI_TEST_FRIENDSHIP.txt`。它遵循当前本地 HOI4 `scripted_gui = { ... }` 形状，包含 context type、window name、parent window token、默认关闭的 `visible` trigger，以及空的 `effects`、`triggers` 和 `properties` blocks。context type、window name、parent window token 和 visibility 都是有默认值的 advanced 字段，所以紧凑创建表单只需要 title。Interface `.gui` layout files、decision-category wiring、dynamic lists、button effects、AI behavior、scripted localization，以及 PIHC2 scripted GUI import 仍然留到后续切片。

创建一个基础 equipment shell：

```python
project.create_module(
    "equipment",
    "EQUIPMENT_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Kit",
        "description": "A compact infantry equipment shell.",
    },
)
```

equipment 模板会写入 `src/modules/equipment/EQUIPMENT_TEST_FRIENDSHIP/`，并通过 PIHC3 项目本地 `equipment` family 构建到 `common/units/equipment/EQUIPMENT_TEST_FRIENDSHIP.txt`。它会创建一个小型 `equipments = { ... }` block，包含当前本地 HOI4 文件中常见的 `year`、`archetype`、`is_archetype`、`picture` 和 `active` 字段；这些都是有默认值的 advanced 字段。PIHC2 equipment import、不同 archetype 的专用 preset、modules、upgrades 和 icon wiring 仍然留到后续切片。

创建一个基础 building shell：

```python
project.create_module(
    "building",
    "BUILDING_TEST_FRIENDSHIP",
    values={
        "title": "Friendship Hall",
        "description": "A compact custom building shell.",
    },
)
```

building 模板会写入 `src/modules/building/BUILDING_TEST_FRIENDSHIP/`，并通过 PIHC3 项目本地 `building` family 构建到 `common/buildings/BUILDING_TEST_FRIENDSHIP.txt`。它会创建一个小型 `buildings = { ... }` block，base cost、value 和 infrastructure construction effect 都是有默认值的 advanced 字段。state placement、slots、map rendering、icons，以及 PIHC2 building import 仍然留到后续切片。
