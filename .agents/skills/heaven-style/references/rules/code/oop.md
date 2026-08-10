---
id: oop
title: OOP vocabulary
enabled: true
blocking: true
order: 30
category: code-quality
keywords: [serialize, as_dict, fetch, retrieve, from_json, CRUD, collection, engine, preset, provider, backend]
description: Use when designing public objects, stores, clients, CRUD/KV APIs, batch APIs, engines, specs, configs, plans, or presets.
---

# OOP vocabulary

## Core rule

Public APIs use one name per concept and type annotations on parameters and returns. Prefer the terms below before inventing alternate names. For whether a concept deserves a public class or function at all, also apply [model.md](model.md).

## Apply when

- Code adds or changes public objects, stores, registries, clients, backends, engines, presets, specs, configs, plans, or CRUD/KV APIs.
- Code uses names like `serialize`, `as_dict`, `fetch`, `retrieve`, `from_json`, `save`, `register`, `load`, `query`, or `search`.

## Do

- Use one canonical method name per concept.
- Prefer Python protocols for collection-like objects before custom accessors.
- Keep retrieval, exact lookup, search, query, and file loading distinct.
- Type public method parameters and returns.

## Avoid

- Synonyms such as `as_dict` and `to_dict` in the same surface.
- `save` for registry, database row, or config writes that persist immediately.
- Free-function front doors when the object model already has a natural class/instance method.

## Serialization and files

Use utility verbs for raw formats:

| Concept | Canonical |
| --- | --- |
| String/bytes conversion | `loads_*`, `dumps_*` |
| File conversion | `load_*`, `dump_*`; object artifact output may use `save(path)` |
| Path constructors | `from_path`, `from_file` |

Avoid `serialize`, `deserialize`, `toJSON`, and ad-hoc file verbs.

Use `save(path)` only for writing a file/artifact owned by the object, such as `LLMImage.save(path)`, or a future `Capsule.save(path)`. Do not use `save` for database rows, registries, workspace registration, or config writes that already persist immediately.

## Exportable objects

| Concept | Canonical |
| --- | --- |
| Build from mapping | `from_dict(cls, data, ...)` |
| Compile class/type from schema | `from_schema(cls, spec, ...)` |
| Export mapping | `to_dict(self)` |
| Copy with patch | `clone(self, **updates)` |
| Class-level retrieval | `load(cls, key=None, ...)` |
| Display | `to_str`, `__str__` delegates to `to_str` |
| UI/API projection | `to_view` |

Use `from_dict` for object/row instances built from data. Use `from_schema` when the input describes a class/type/schema rather than one row, for example `hb.Entity.from_schema({...})`.

Use `load` as the class-level retrieval verb for public objects that can be reopened from a registry, cache, store, or configured default, for example `hb.HeavenBase.load("shop")`, `Prompt.load("name")`, or `BackendType.load("sqlite")`. If a class supports both registry lookup and file loading, make file loading explicit with `path=`/`file=` or `from_path`/`from_file`; never infer registry-vs-file meaning from a bare string.

## Collections

Collection-like objects should implement Python protocols first, then explicit exports:

```python
def __len__(self) -> int: ...
def __iter__(self): ...
def __getitem__(self, key: str) -> Row: ...
def to_list(self) -> list[dict[str, object]]: ...
def to_dict(self) -> dict[str, object]: ...
```

Use `add` for mutating in-memory collections, builder lists, or runtime registries when the object is already in memory and no durable global registration happens, for example `Toolkit.add(...)`, or `InteropReport.add(...)`. Prefer collection protocols plus `get`/`__getitem__` for read access.

## Registries and workspace-bound objects

Use `register` when the operation makes an object discoverable in a database, workspace, Python registry, or capability registry:

```python
ws.register(Entity)
capsule.register()
toolkit.register()
HeavenBase.load("shop")
# pseudocode — use the repo's handler registration API
register_handler(...)
register_backend(...)
```

Do not use `save` for registry writes. Registry-oriented classes should expose OOP class/instance methods such as `HeavenBase.load`, `HeavenBase.register`, `Capsule.register`, `Toolkit.register`, and `Capsule.verify`, not free-function front doors like `get_workspace`, `register_workspace`, or `verify_manifest`.

## CRUD and search

| Concept | Canonical |
| --- | --- |
| Create only | `insert` |
| Merge/create by key | `upsert` |
| Delete one | `remove` |
| Delete all | `clear` |
| Rename | `rename` |
| Exact single lookup | `get` |
| External retrieval / RAG retrieval | `retrieve` |
| Structured query | `query` |
| Fuzzy or ranked lookup | `search` |

`get` is for exact lookup. `retrieve` is acceptable when the domain means retrieval rather than key access.

## KV CRUD

Use `get`, `set`, `unset`, `setdef`, `clear`, and optionally `__getitem__` / `__setitem__` for natural mapping syntax.

```python
cache.set("token", value)
value = cache.get("token", default=None)
cache.unset("token")
```

Native `dict.get` uses positional fallback; project KV objects may support `default=`.

## Batch verbs

Use `batch_*` when the batch behavior is not equivalent to looping because it changes I/O, transactionality, routing, or performance:

```python
store.batch_upsert(rows)
rows = store.batch_get(ids)
```

## Engines and lifecycle

Use `connect`, `close`, `flush`, `drop`, `start`, `stop`, and `reset` for lifecycle verbs. `drop` is destructive schema/storage removal; `clear` removes contents but keeps the object.

## Specs, configs, plans

- `*Spec`: declarative input contract or normalized request.
- `*Config`: runtime settings and defaults.
- `*Plan`: ordered execution decision.
- `*Engine`: stateful executor or connection-owning runtime.
- `identifier`: stable type/class identifier.
- `object_id`: user-facing object identity.
- `type`: external schema word only; prefer `kind`, `dtype`, or `entity` in Python when clearer.
- `metadata`: opaque extra user/provider data; avoid hiding required fields in it.
- `canonical`: normalized single source of truth.

## Preset system

Use this hierarchy when modeling configurable backends:

```text
Preset = Provider + params
Provider = customizable backend route + provider defaults
Backend = concrete dialect/driver/runtime implementation
```

For LLMs, a preset is a directly callable config containing provider, model, gateway, and model args. Provider plus gateway determines the backend route; model args tune a request.

For databases, a preset is a named database/provider config. A provider describes an engine family with backend, dialect/driver, and connection args. A backend is the implementation adapter.

## Example

```python
class Row:
    def as_dict(self):
        return dict(self._data)

    def fetch(self, key):
        return self._data[key]
```

```python
from typing import Any

class Row:
    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Row":
        return cls(data)

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def clone(self, **updates: Any) -> "Row":
        return type(self)({**self._data, **updates})

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)
```

## Related rules

Also apply [model.md](model.md) for public surface size, [name.md](name.md) for symbol naming, [types.md](types.md) for annotations, and [config.md](config.md) for provider/preset defaults.
