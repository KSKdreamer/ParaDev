---
id: model
title: Mental model
enabled: true
blocking: true
order: 35
category: code-quality
keywords: [api surface, class count, function count, DSL, user model, interface design, abstraction, constructor flags, OOP front door]
description: Use when adding public classes or functions, designing a user-facing surface, choosing method versus free function, adding constructor flags, or proposing a DSL.
---

# Mental model

## Core rule

Keep the public OOP interface as small as possible. For each functionality, expose the shortest owning-object flow: classmethods create or load objects, instance methods perform lifecycle actions, and common code reads as `obj = Class(...); obj.verb()` or `Class.from_dict(...).verb()`. Do not introduce public classes, free functions, constructor flags, or DSL syntax unless they remove real complexity for users.

## Apply when

- Code adds public classes, functions, modules, decorators, DSL syntax, or user-facing data structures.
- A feature can be represented as either an object method, classmethod, free function, or new wrapper class.
- A proposed abstraction adds a new concept users must learn.
- A constructor grows flags that perform a second lifecycle action, such as registering, setting a default, isolating global state, verifying, or opening resources.
- A public example requires nested helper calls, low-level extension namespaces, or multiple imports before the user reaches the domain object.

## Do

- Prefer existing object methods or classmethods over parallel free functions.
- Put behavior on the object that owns the state: `from_dict`, `from_schema`, and `load` create or reopen objects; `register`, `set_default`, `verify`, `connect`, and `close` act on those objects.
- Keep constructors focused on identity and essential configuration. Move optional lifecycle side effects to explicit methods.
- Prefer familiar Python protocols and industrial interfaces over invented mini-languages.
- Keep one clear data container with structured attributes when extra wrapper classes add no behavior.
- Use dedicated classes only for behavior, invariants, lifecycle, or recognized domain concepts.
- Keep low-level registries and extension functions available only as implementation surfaces when needed; public docs and examples should start from `heavenbase as hb` and the owning object.
- Use the reviewer gate for each public API change: the happy path must fit one short OOP sentence, such as "create the object, then call the lifecycle verb", "build the spec from a dict, then register it", or "load the named object, then mutate or query it".
- Require a reviewer or architect justification when a new top-level function, nested helper, or constructor flag is easier to implement but harder to teach. The burden of proof is on the larger surface, not on the shorter OOP path.

## Avoid

- Parallel APIs that do the same thing.
- Constructor flags that hide follow-up actions, especially private-looking flags such as `_register_global=False`, `_set_default=True`, or `_isolated=False` in user-facing flows.
- Nested functional pipelines such as `register_x(build_x(...))` when the same flow can be `X.from_dict(...).register()`.
- Thin public classes that only rename one field.
- Public examples that force users through `hb.ext.*`, registry internals, or helper factories before they see the core domain object.
- DSLs where dictionaries, ORM-style expressions, or ordinary Python would be clearer.

## Example

### Constructor side effects

**Anti-pattern:**

```python
ws = hb.HeavenBase("shop", preset="debug", _isolated=False, _register_global=False, _set_default=True)
```

**Pattern:**

```python
ws = hb.HeavenBase("shop", preset="debug")
ws.set_default()
```

Constructor flags are acceptable only for essential construction policy. Lifecycle actions such as becoming the default workspace should be ordinary verbs.

### Build and register

**Anti-pattern:**

```python
hb.ext.register_profile(
    hb.ext.profile_spec_from_mapping(
        {
            "name": "agent",
            "tools": ["query", "search"],
        }
    )
)
```

**Pattern:**

```python
hb.ProfileSpec.from_dict(
    {
        "name": "agent",
        "tools": ["query", "search"],
    }
).register()
```

The spec owns construction from a mapping and registration into its registry. The user should not have to compose extension helper functions for the common path.

### Register an entity

**Anti-pattern:**

```python
class EntityRegistry:
    def register_entity(self, entity: type["Entity"]) -> None: ...

registry.register_entity(Product)
```

**Pattern:**

```python
ws.register(Product)
```

When registration belongs to a workspace, keep the workspace as the owner. When registration belongs to the class or instance itself, expose `register` there:

```python
capsule.register()
toolkit.register()
```

### Fluent field declaration

**Anti-pattern:**

```python
sku = hb.field(hb.ShortText, store_to="sql", compute_fn=normalize_sku, description="Stock keeping unit")
```

**Pattern:**

```python
sku = hb.field(hb.ShortText).store(to="sql").compute(normalize_sku).desc("Stock keeping unit")
```

Use chained methods when each step configures the same object and keeps the names discoverable in autocomplete.

### Data containers

**Anti-pattern:**

```python
class MetadataAttribute: ...
class Metadata: ...
class Data:
    metadata: Metadata
```

**Pattern:**

```python
class Data:
    metadata: dict[str, object]

value = data.metadata["attr"]
```

Use a dedicated class only when it carries behavior, invariants, lifecycle, or a widely recognized domain concept. If the class only names one field, keep it as a field.

## Related rules

Also apply [oop.md](oop.md) for method vocabulary, [name.md](name.md) for symbols, [types.md](types.md) for public contracts, and [clean.md](clean.md) for helper abstraction costs.
