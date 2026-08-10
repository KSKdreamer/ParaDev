---
id: py
title: Python shape
enabled: true
blocking: true
order: 50
category: code-quality
keywords: [comprehension, ternary, guard clause, compact python, dict get, nested loop, early return]
description: Use when code shape is verbose, deeply nested, unclear, or depends on fallback/control-flow semantics.
---

# Python shape

## Core rule

Prefer comprehensions, guard clauses, unpacking, and direct returns when they keep behavior readable. Do not compress regex bodies, SQL, prompts, long error messages, or branching that needs operator context.

For tiny helper functions that only hide a one-line transform, also apply [clean.md](clean.md).

## Apply when

- Code builds lists/dicts/sets through append loops.
- Code is deeply nested or lacks early returns.
- Code uses fallback reads such as `dict.get`, config helpers, or `or` defaults.
- A helper only hides a one-line transformation.

## Do

- Use comprehensions for simple filter/map operations.
- Use guard clauses for invalid or empty paths.
- Keep fallback semantics explicit.
- Prefer direct returns for simple expressions.

## Avoid

- Compressing multi-branch business logic into dense expressions.
- `or` defaults when falsy caller values are valid.
- Helpers that make readers jump for no real reuse.

## Example

```python
out = []
for item in items:
    if item.get("active"):
        out.append(item["name"].lower())
```

```python
out = [item["name"].lower() for item in items if item.get("active", False)]
```

Use explicit fallback semantics. Native `dict.get` takes the fallback positionally; config helpers use `default=`.

## Related rules

Also apply [config.md](config.md) for config defaults, [types.md](types.md) for annotations, and [clean.md](clean.md) for helper decisions.
