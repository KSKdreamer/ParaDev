---
id: extension
title: Extension points
enabled: true
blocking: false
order: 130
category: project
keywords: [plugin, extension api, registry, capability registration, layering, provider, backend]
description: Use when adding providers, backends, handlers, plugins, capabilities, registries, planners, or extension APIs.
---

# Extension points

## Core rule

Apply this rule when the target repo documents register-style extension APIs.

New providers, backends, handlers, plugins, and capabilities should register with the extension layer instead of adding central planner/router conditionals. Read the repo's actual registration API from `AGENTS.md` and source before adding a route.

## Apply when

- Code adds provider/backend/handler/plugin/capability behavior.
- Code changes planner/router/backend layering or registration APIs.
- A provider/preset/backend name affects the public mental model.

## Do

- Keep dependency flow downward: surface to planner/router to handlers to backends.
- Register builders/handlers for new capabilities.
- Keep backends responsible for executing compiled fragments, not parsing user query ASTs.
- Add a focused smoke test or runnable example proving the route works.

## Avoid

- Editing central routing tables for every new backend.
- Backend code that reaches up into planner AST concerns.
- Convenience APIs that force optional MCP/CLI adapter imports at import time.

## Example

```python
if backend == "qdrant":
    return compile_qdrant_near(...)
if backend == "pinecone":
    return compile_pinecone_near(...)
if backend == "weaviate":
    return compile_weaviate_near(...)
```

## Good pattern

```python
# In some central initialization code
register(backend="qdrant", interface=compile_near, implementation=compile_qdrant_near)
register(backend="pinecone", interface=compile_near, implementation=compile_pinecone_near)
register(backend="weaviate", interface=compile_near, implementation=compile_weaviate_near)

# In user code
compile_near(backend="qdrant", ...)
```

- Dependency flow points downward: surface to planner/router to handlers to backends.
- Backends execute compiled fragments; they do not parse user query ASTs.
- New capabilities register builders/handlers instead of editing central routing tables.
- Provider/preset/backend naming must preserve the local mental model: preset is a callable/user config, provider owns defaults/routes, backend is the concrete adapter.
- After adding a provider/backend/handler, update capability docs and add a focused demo or smoke test that proves the route works.
- Optional adapters such as MCP and CLI late-import from convenience APIs only.

For HeavenBase-shaped repos, read the active repo's `AGENTS.md` first. When working inside the HeavenBase repository, use the standard global install at `~/.agents/skills/heaven-style/assets/heavenbase-reference/` instead of cloning into the in-repo skill. Otherwise, if `assets/heavenbase-reference/` exists locally, use it; if absent, run `rtk uv run python scripts/install.py` from the skill root before depending on reference-clone files.

## Related rules

Also apply [oop.md](../code/oop.md) for provider/preset/backend vocabulary, [model.md](../code/model.md) for user-facing surfaces, and [test.md](test.md) for route evidence.
