# Project Manifest

Status: active schema note

Date: 2026-06-06

Purpose: define the first `paradev.yaml` contract used by `Project.load(path)` and CLI project inspection.

## Minimal Schema

```yaml
project_id: minimal_hoi4
title: Minimal HOI4 Project
game: hoi4
source_roots:
  - src
build_root: .paradev/.cache/build
```

## Fields

| Field | Required | Meaning |
| --- | --- | --- |
| `project_id` | yes | Stable project identifier used in manifests and future HeavenBase rows. |
| `title` | yes | Human-facing project name for CLI, desktop, MCP, and reports. |
| `game` | yes | Target game package identifier, initially `hoi4`. |
| `preferred_language` | no | Project-wide authoring language. ParaDev accepts HoI4 aliases such as `l_simp_chinese`, but persists one compact value such as `en` or `zh`; the default is `en`. `Project.templates()`, SDK/REST/MCP module creation, and desktop create forms resolve omitted localization language from this value; an explicit create value still wins. |
| `source_roots` | yes | Non-empty list of authored source directories, resolved relative to the manifest root. |
| `output_root` | no | Game-ready generated output root, resolved relative to the manifest root. When omitted for HoI4 on macOS, defaults to `~/Documents/Paradox Interactive/Hearts of Iron IV/mod/<project_id>`; on other platforms it falls back to `build/mod`. |
| `build_root` | yes | ParaDev build metadata root, resolved relative to the manifest root. |
| `families` | no | Project-local declarative family declarations for simple, routed, and collection compilers. |
| `python_modules` | no | Trusted project-local Python files that extend the selected build registry through `register(registry)`. |
| `copy_roots` | no | External or project-local compatibility file trees copied into build output before generated artifacts are applied. |
| `mod_version` | no | HoI4 descriptor version field. Defaults to the profile value when omitted. A leading `v` is normalized out for HoI4 descriptors. |
| `supported_version` | no | HoI4 descriptor supported game version field. Defaults to the profile value when omitted. |
| `picture` | no | HoI4 descriptor picture field, usually a thumbnail path copied into the output root. |
| `remote_file_id` | no | Optional Steam Workshop file id for HoI4 descriptors that should match an existing published mod. |
| `tags` | no | HoI4 descriptor tag list. |
| `replace_path` | no | HoI4 descriptor replace-path list. |

## Discovery

`Project.load(path)` accepts either the project root or a nested file or folder. It walks upward until it finds `paradev.yaml`, then resolves all manifest paths from that root.

When `output_root` is omitted, ParaDev chooses the profile default. For HoI4 on macOS this is the user mod folder at `~/Documents/Paradox Interactive/Hearts of Iron IV/mod/<project_id>`, so `--emit-artifacts` produces a launcher-ready mod folder by default. Set `output_root` explicitly when a project needs a local reproducible output such as `build/mod`.

Missing or invalid manifests raise a contextual project-manifest error. Basic loading does not require a database; HeavenBase indexing starts after project discovery and build records are stable.

`preferred_language` is an author-facing choice and therefore belongs in the
visible manifest when a project is not English-first. Individual extension
descriptors may retain portable fallback defaults, but the loaded Project
resolves one effective language before exposing templates to SDK, REST, MCP,
or desktop consumers. Module authors do not repeat it in `meta.yaml`. Ordinary
users can change it through **Settings → Authoring defaults → Project
language**; automation can use `Project.set_preferred_language(...)` or
`paradev project-language`, both of which use the same reviewed plan/apply
transaction.

## Registry Extensions

New project-owned module types should use one cohesive
`extensions/<family>/` folder. Editable Entity, compiler, and provider code
lives in `__init__.py`; generated Registry metadata lives in
`.paradev/meta.yaml`. ParaDev stages that folder as a standard HeavenBase
module artifact and installs it through the same 0.1.2.2 Registry path as an
external bundle. A standard root-level `meta.yaml` is still accepted for
ordinary HeavenBase bundles, but one extension cannot contain both locations.

The older manifest-level `families` and `python_modules` fields remain
compatibility inputs for existing projects; they are not the recommended
PIHC3 authoring architecture. Simple declarative family declarations can emit
copied assets and optional sprite GFX declarations by combining
`templates.copy`, `templates.sprite_gfx`, `templates.sprite_name`, and
`sprite_slots`. All sprite template fields are validated together so a family
cannot silently skip sprite emission because one part is missing. If two
selected copied sources render the same sprite name, builds report a blocking
`<family>.duplicate_sprite_name` diagnostic against the later source.

Publication migration state does not belong in `paradev.yaml` or a compiler
constructor. A standalone Registry extension may put this generated metadata
on its `paradev_build_family` item:

```yaml
meta:
  publication:
    replaces_families:
      - older_family_id
```

ParaDev reads that value from HeavenBase's inert Registry record before
importing the compiler. It is not a discovery alias: only a family-wide
targeted artifact build reconciles tracked rows for those replaced ids. Module
and collection targets never broaden their cleanup scope. A replaced id cannot
be active, name the successor itself, or be claimed by more than one active
family. Hidden project descriptors are generated system state; ordinary module
authors do not maintain this declaration.

Projects list family Python files under `python_modules`:

```yaml
python_modules:
  - tools/families/superevent.py
  - tools/families/news_event.py
```

Each path resolves relative to the manifest root, must stay inside the project, and must point to an existing `.py` file. ParaDev imports each file as trusted local project code and calls a callable `register(registry)`. The function can mutate the supplied registry or return a `BuildRegistry`.

Manifest registry extensions are applied only when SDK and CLI callers use the selected profile registry. SDK callers that pass an explicit `registry=` receive that registry as-is.

## Copy Roots

`copy_roots` are for projects that need to integrate existing compiled mod files before every domain has native ParaDev source. Each copy root plans static-copy artifacts from a source directory into the selected artifact target root:

```yaml
copy_roots:
  - id: legacy
    source: /absolute/or/project-relative/path/to/compiled-mod
    target: .
    target_root: output
    include:
      - common/**
      - events/**
      - gfx/**
      - interface/**
      - localisation/**
    exclude:
      - descriptor.mod
```

`source` may be absolute or relative to the project root. `target` is relative to the selected target root and defaults to `.`. `target_root` is `output` by default and may also be `build`. Include/exclude entries are POSIX-style glob patterns relative to the copy root source.

Copy roots are a compatibility baseline. If a generated artifact and copied file target the same output path, the generated artifact wins and the build records a non-blocking `copy_root.shadowed_artifact` warning. This lets migration projects keep a runnable copied baseline while replacing legacy roots with native ParaDev modules incrementally.
