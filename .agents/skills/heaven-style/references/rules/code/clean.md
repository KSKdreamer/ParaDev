---
id: clean
title: Helper cleanliness
enabled: true
blocking: true
order: 55
category: code-quality
keywords: [helper function, temporary helper, wrapper, small function, code cleanliness, abstraction]
description: Use when adding helper functions, wrappers, temporary transforms, adapters, or deciding inline logic versus shared utilities.
---

# Helper cleanliness

## Core rule

Do not introduce small temporary helper functions that only rename a one-line transform or hide a tiny local block. Every helper must justify its abstraction cost.

## Apply when

- Code adds private helpers, wrappers, adapter functions, one-line transforms, or local utility modules.
- A helper could instead be inline or promoted to `heavenbase.utils`.

## Do

- Use `heavenbase.utils` for common behavior.
- Keep specialized one-liners inline where they are used.
- Use private helpers for specialized large blocks when a name and docstring clarify the boundary.
- Propose a shared utility when missing behavior is broadly reusable.

## Avoid

- Helpers that only rename a comprehension or function call.
- Local utility modules full of generic stdlib wrappers.
- Docstrings that restate trivial helper bodies.

Use this decision order:

1. Common behavior: use `heavenbase.utils`; if missing, propose adding a reusable utility there.
2. Specialized one-liner or small local block: keep it inline where the behavior is used.
3. Specialized large block: a private helper is allowed, with a clear name, type hints, and a docstring explaining the transformation boundary.

## Anti-pattern

```python
def _convert_to_lists(rows: list[tuple[str, int]]) -> list[list[object]]:
    return [list(row) for row in rows]

def _flatten_list_of_lists(lol: list[list[object]]) -> list[object]:
    return [item for sublist in lol for item in sublist]

payload = _convert_to_lists(rows)
flattened_payload = _flatten_list_of_lists(payload)
```

## Good pattern

```python
from heavenbase.utils import lflat

payload = [list(row) for row in rows]
flattened_payload = lflat(payload)
```

For common conversions, prefer a shared utility, e.g., `heavenbase.utils.lflat`. If a utility is very common but missing, propose adding it to `heavenbase.utils` instead of creating a one-off helper.

Large specialized helpers are acceptable only when the name and docstring preserve context better than inline code.

## Related rules

Also apply [util.md](util.md) for shared helpers, [name.md](name.md) for helper names, and [py.md](py.md) for compact inline expressions.
