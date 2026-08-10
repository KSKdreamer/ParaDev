---
id: overview
title: Rule overview
enabled: true
blocking: true
order: 1
category: overview
keywords: [which rule, what rules apply, rule map, style overview, start here]
description: Use when deciding which heaven-style rule files apply to a task.
---

# Rule overview

Rule frontmatter uses `description` and `keywords` to help agents find relevant files. The Markdown body is the source of truth for behavior.

Each rule uses this body shape where practical:

1. `Core rule` - the normative rule.
2. `Apply when` - situations that should load the rule.
3. `Do` - preferred behavior.
4. `Avoid` - banned or discouraged behavior.
5. `Example` - focused anti-pattern and good-pattern pairs when useful.
6. `Related rules` - cross-rule checks.

## Code-quality rules

1. `util` - load for imports, file I/O, JSON/YAML/pickle/text, shell, logging, hashing, temp paths, or deterministic IDs.
2. `config` - load for tunables, defaults, prompts, templates, resources, paths, model/provider/backend parameters, or disputed literals.
3. `types` - load for public APIs, `typing` imports, Python-version compatibility, dict/list annotations, or schema-shaped data.
4. `oop` - load for public method names, entity/store/client APIs, CRUD, KV, batch, engine lifecycle, specs/configs/plans, or preset/provider/backend models.
5. `model` - load for public API surface design, new classes/functions, user mental models, or DSL/interface choices.
6. `name` - load for naming reviews, new public symbols, abbreviations, module names, or glossary changes.
7. `py` - load for Python control-flow shape, comprehensions, guard clauses, and fallback semantics.
8. `clean` - load when adding helper functions, wrappers, adapters, temporary transforms, or abstraction boundaries.
9. `error` - load for validation, unsupported choices, exception boundaries, logging, or swallowed errors.
10. `sql` - load for database access, raw SQL, migrations, DDL, ORM use, and bind parameters.
11. `compat` - load for renames, deprecations, migration shims, `v1/v2` splits, or config schema changes.

## Project rules

1. `environment` - load when running shell commands, choosing `uv`/Python, adding Bash wrappers, or fixing wrong-environment failures for coding agents.
2. `format` - load when running or reviewing lint, format, import order, or repo command wrappers.
3. `test` - load when adding behavior, tests, examples, smoke checks, provider routes, or LLM/MCP integration evidence.
4. `docs` - load when changing user-facing APIs, Mintlify pages, sibling docs repos, generated artifacts, Linear status, release notes, or commits.
5. `review` - load for PR/diff review, inline comments, waivers, or final quality gates.
6. `extension` - load when adding plugin/provider/backend/handler capabilities to a registry-based project.

Examples live inside their owning rules. Do not add a separate demo rule surface unless a future project has concrete evidence that search/routing works better with separate example files.

## Failure playbooks

Use `references/failures/` when command failures block progress:

1. `failure-env` - Python, `uv`, shell, PATH, or wrong environment failures.
2. `failure-network-proxy` - CLI/API network failures, VPN/proxy ambiguity, or provider connectivity.
3. `failure-auth-secrets` - MCP/provider auth expiry, missing API keys, Linear/Tavily/LLM token failures, or direct API fallback.
4. `failure-linear-pressure` - Linear project issue limits, noisy progress comments, or stale Done/Duplicated/Outdated issue cleanup.
