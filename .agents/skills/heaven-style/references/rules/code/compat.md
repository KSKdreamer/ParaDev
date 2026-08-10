---
id: compat
title: Compatibility shims
enabled: true
blocking: true
order: 90
category: code-quality
keywords: [deprecated, shim, v1 v2, warnings.warn, backward compatibility, alias, migration]
description: Use when renaming APIs, changing config schemas, adding aliases, preserving old behavior, or proposing migration/deprecation shims.
---

# Compatibility shims

## Core rule

Prefer one live API version. Rename freely and update call sites in the same change.

## Apply when

- Code renames APIs, config keys, modules, imports, or public methods.
- A change proposes aliases, wrappers, deprecation warnings, v1/v2 modules, or migration branches.
- Predecessor project compatibility is being preserved or removed.

## Do

- Update call sites to the cleaner API in the same change.
- Keep one config schema and update defaults/bootstrap when keys change.
- Put one-shot migrations under scripts or migrations.
- Document explicit compatibility waivers when the user requires a layer.

## Avoid

- Permanent `warnings.warn` shims.
- Parallel `v1` / `v2` modules.
- Old imports/dependencies that duplicate the new API.
- Permanent library branches for one-time migrations.

## Example

```python
def old_api(value: str) -> str:
    warnings.warn("old_api is deprecated; use new_api", DeprecationWarning)
    return new_api(value)
```

## Legacy lineage

`pyheaven`, `heaven`, and `AgentHeaven` are predecessor names for the HeavenBase package and lineage. Treat **HeavenBase** as the current public name and API surface.

When migrating or reviewing older docs, issues, imports, or sibling repos:

- Map legacy names to HeavenBase equivalents.
- Verify feature parity through the new cleaner API.
- Remove old dependency/import paths in the same change unless explicitly waived.

## Good pattern

```python
def new_api(value: str) -> str:
    ...
```

- Waiver only when the user explicitly requests a documented compatibility layer.

## Related rules

Also apply [model.md](model.md) for one clear API, [name.md](name.md) for renamed symbols, [config.md](config.md) for schema changes, and [docs](../project/docs.md) for migration notes.
