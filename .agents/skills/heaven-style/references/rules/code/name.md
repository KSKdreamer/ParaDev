---
id: name
title: Names
enabled: true
blocking: true
order: 40
category: code-quality
keywords: [rename, naming, glossary, abbreviations, snake_case, terse, variable name]
description: Use when adding or reviewing modules, public symbols, abbreviations, predicates, variable names, or glossary terms.
---

# Names

## Core rule

Names should be short enough for hot-path readability and precise enough to preserve meaning. Use one word per concept and keep new abbreviations explicit in the change that introduces them.

## Apply when

- Code adds or renames modules, functions, classes, variables, config keys, predicates, or glossary terms.
- Code introduces abbreviations or chooses between alternate-name-heavy API names.

## Do

- Hot-path symbols are short; leaf helpers may be longer.
- `snake_case` functions/modules/vars; `PascalCase` classes; `SCREAMING_SNAKE` for `CM_*` singletons.
- Verb-first: `load_json`, `parse_spec`; registration helpers may read like `# pseudocode: register_handler(...)`.
- Predicates: `is_*`, `has_*`, `can_*`.

## Avoid

- Type suffixes such as `user_list`.
- Invented abbreviations without a local glossary.
- Redundant phrases like `database_connection_object_list`.

## Example

```python
database_connection_object_list = load_database_connections()
```

```python
dbs = load_dbs()
```

## Shared abbreviations

| Long | Short |
| --- | --- |
| Config manager | `CM_<PKG>` |
| Path join | `pj` |
| Database | `db` |
| Embedding | `emb` |
| Count / limit | `n_*`, `max_*` |
| Specification | `*Spec` |

Invented abbreviations belong in the same PR that introduces them. Framework-specific glossaries live in reference assets when needed.

## Related rules

Also apply [oop.md](oop.md) for canonical method names and [model.md](model.md) when naming reveals an unnecessary public concept.
