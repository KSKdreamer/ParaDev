# PIHC3 Source Cutover

Status: current source-authority boundary

Date: 2026-08-03

PIHC3's import migration is complete. Historical importer inventories and
intermediate component layouts are not current project architecture. Git
history and dated progress notes retain that evidence; active documentation
describes only the semantic source model below.

## One Authoring Layout

Every independently editable object lives at:

```text
projects/PIHC3/src/modules/<family>/<id> - <preferred-language title>/
```

A collection exists only when sibling context is a real compiler concept:

```text
projects/PIHC3/src/collections/<family>/<id> - <preferred-language title>/
```

The module or collection folder is the single source of truth for its
definition, localization, preview image, compiled icons, and other resources.
Those resources are ordinary slots declared by the registered family. A
project-local HeavenBase Entity is needed only for a genuinely project-owned
persistence type; built-in HoI4 families use compiler overlays without
redefining their canonical Entity. Resources never require a parallel asset
family.

The live project forbids:

- family or source directories ending in `_component` or
  `_asset_component`;
- `legacy/` and `inactive_modules/` source trees;
- object ids containing retired component markers;
- source-unit names that do not use `id - title`;
- visible compiler-owned metadata.

Use `inactive: true` in the exceptional module that must remain authored but
must not compile. Normal modules need no visible `meta.yaml`; folder identity,
authored resources, and Registry declarations provide compiler-owned facts.

## Extension Ownership

Project-specific behavior lives cohesively at:

```text
projects/PIHC3/extensions/<family>/
```

Each extension publishes a versioned descriptor, registers through the same
ParaDev/HeavenBase Registry path as bundled families, and owns its resource
slots, validation, normalization, aggregation, artifact emission, authoring
hints, and optional diagram capability. Built-in HoI4 types use thin compiler
overlays; only genuinely PIHC3-specific persistence types own project-local
Entities. PIHC3-only types such as Inventory Item, State Lore, and Superevent
remain project-local extensions; the ParaDev core does not route them by name.

## Canonical Semantic Owners

Assets and former aggregate support files now belong to their semantic owner.
Examples include:

| Content | Canonical owner |
| --- | --- |
| Achievement definitions and icon variants | `achievement` |
| Country definitions, flags, and previews | `country` |
| Country history | `country_history` |
| Decision definitions, categories, previews, and icons | `decision` |
| Focus definitions, tree relationships, previews, and compiled icons | `focus` |
| Technology definitions, tree relationships, previews, and compiled icons | `technology` |
| Character portraits | `character` or the standalone `portrait` family |
| Static game resources without a richer semantic owner | `game_asset` |
| AI configuration and shared game data | `ai_config` and `common_data` |
| MIO definitions and tree relationships | `military_industrial_organization` |

This table is an authoring guide, not a dispatch table. Registry descriptors,
registered compiler families, and the canonical Entity contracts are
authoritative at runtime.

## Mechanical Gate

Run the source audit before building:

```bash
rtk uv run python projects/PIHC3/scripts/check_source_layout.py --json
```

The audit walks the physical project tree, ignores Git's object database, and
fails on every retired directory, malformed source-unit name, source symlink,
copy-marker folder, or visible system metadata field. PIHC3 regression tests
also cover canonical resource ownership and the clean/full, cached,
family-partial, and module-partial compiler paths.

Git can still display retired files from an older commit or from its index
while their deletion is uncommitted. Such entries are repository history, not
live compilation sources. A completed cutover commit is what removes them from
a clean checkout; restoring those deleted paths would reintroduce invalid
source.

Use the [PIHC3 project guide](../../projects/PIHC3/README.md), the
[PIHC3 migration cutover note](../../projects/PIHC3/docs/migration/README.md),
and the [PIHC3 user manual](../user-manual/pihc3.md) for current workflows.
