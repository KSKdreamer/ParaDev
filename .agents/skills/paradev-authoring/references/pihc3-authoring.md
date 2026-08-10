# PIHC3 Authoring Routes

Read this reference when a PIHC3 request involves a collection, tree, or a
content type beyond the focused idea example.

The live `project_templates` result is authoritative. Query it with
`source="project"` and `authoring_ready=true`, then use its exact `args`,
descriptions, defaults, and file list. The template ids below are routing hints,
not schemas; confirm each id before planning. Never synthesize visible metadata
or assume an icon, localization, or definition filename.

| User intent | Kind and family | Current template hint |
| --- | --- | --- |
| Achievement | module `achievement` | `pihc3:achievement/basic` |
| Character | module `character` | `pihc3:character/basic` |
| Country | module `country` | `pihc3:country/basic` |
| Decision category | collection `decision` | `pihc3:decision-category/basic` |
| Decision | module `decision` | `pihc3:decision/basic` |
| Division template | module `division` | `pihc3:division/basic` |
| Doctrine root or node | module `doctrine` | `pihc3:doctrine/grand-basic` or `pihc3:doctrine/subdoctrine-basic` |
| Equipment | module `equipment` | `pihc3:equipment/basic` |
| Event | module `event` | `pihc3:event/country-basic` |
| Focus tree | collection `focus` | `pihc3:focus-tree/basic` |
| Focus node | module `focus` | `pihc3:focus/basic` |
| Idea | module `idea` | `pihc3:idea/basic` |
| Military industrial organization | module `military_industrial_organization` | `pihc3:military_industrial_organization/basic` |
| Modifier | module `modifier` | `pihc3:modifier/basic` |
| State | module `state` | `pihc3:state/basic` |
| Technology | module `technology` | `pihc3:technology/basic` |
| Inventory item extension | module `inventory_item` | `pihc3:inventory_item/basic` |
| State lore extension | module `state_lore` | `pihc3:state_lore/basic` |
| Superevent extension | module `superevent` | `pihc3:superevent/basic` |

Treat category/tree containers as collections and their independently editable
content as modules. In particular, create a Focus tree collection separately
from its Focus nodes, and create a Decision category collection separately from
its Decision modules. Use `module_collection_set` for reviewed membership
changes instead of editing system metadata.

Use the diagram family ids `focus`, `technology`, `doctrine`, and
`military_industrial_organization` for source-backed graph discovery and edits.
Read `browser.families[].diagram.node_authoring` before constructing node
intents; node fields belong to the registered provider, not this reference.

For localization, use `localization_workspace` and `localization_plan` for both
modules and collections. For images and copied resources, use only the exact
Registry-owned slots returned by `project_browser`; module binary replacements
must be guarded with `module_asset` and `project_draft_apply`. A missing slot is
an unsupported resource, not permission to invent a path.
