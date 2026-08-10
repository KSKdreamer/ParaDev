---
id: format
title: Imports and formatting
enabled: true
blocking: true
order: 100
category: project
keywords: [import order, line length, flake, black, repo script, wrapper]
description: Use when running or reviewing formatters, linters, import order, line length, generated compatibility files, or command wrappers.
---

# Imports and formatting

## Core rule

Use the repository's declared entrypoints (`scripts/flake.bash`, `Makefile`, `pyproject.toml`, or equivalent). Do not bypass wrappers with bare tools when wrappers exist. For `rtk`, `uv`, `AGENTS.md`, and `_env.bash` policy, apply [environment.md](environment.md) first.

## Apply when

- Running or reviewing formatting, linting, import order, line length, generated compatibility files, or command wrappers.
- Deciding whether to call Black/Flake8/Pytest directly or through repo scripts.

## Do

- Use repo wrappers such as `scripts/flake.bash`, `scripts/test.bash`, or `Makefile` targets.
- Keep tool configuration in `pyproject.toml` when supported.
- Alphabetize imports within groups and remove unused imports.

## Avoid

- Bare tools when wrappers exist.
- New setup files such as `pytest.ini` or `setup.cfg` unless the tool cannot read `pyproject.toml`.
- Star imports except explicit project utility boilerplate where already established.

## Example

```bash
black src
pytest
```

## Good pattern

```bash
rtk bash scripts/sync-env.bash
rtk bash scripts/flake.bash -a
rtk bash scripts/test.bash
```

## Import order

1. Project utility re-exports.
2. First-party submodules.
3. Third-party packages.
4. Stdlib that is not covered by HeavenBase utilities.

Alphabetize within groups. Remove unused imports. Avoid star imports except explicit utility boilerplate when the project already uses it.

## Related rules

Also apply [environment.md](environment.md) for `rtk`/`uv` command policy, [test.md](test.md) for test wrappers, and [util.md](../code/util.md) when import cleanup touches utility-covered stdlib.
