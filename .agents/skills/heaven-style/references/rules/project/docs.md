---
id: docs
title: Docs and generated content
enabled: true
blocking: false
order: 120
category: project
keywords: [README, generated docs, doc sync, mintlify, docs json, architecture docs, translation, examples]
description: Use when public behavior, README content, user-facing docs, generated docs, Mintlify pages, sibling docs repos, or translation staleness changes.
---

# Docs and generated content

## Core rule

Docs, examples, generated artifacts, architecture notes, sibling docs repos, and translation state must match the implementation.

## Apply when

- Code changes public behavior, README claims, architecture notes, generated artifacts, examples in rules, or user-facing docs.
- Mintlify or sibling docs repos need sync.
- English docs changed and translated pages may now be stale.

## Do

- Verify docs claims against current source, tests, examples, and generated outputs.
- Sync user-facing docs and sibling docs repos when public behavior changes.
- Regenerate generated docs when the repo provides generators.
- Keep canonical docs sources clear, such as `README.en.md` generating `README.md`.
- Report stale translated pages and route translation work to the dedicated translation task.

## Avoid

- Docs that describe planned behavior as shipped.
- Folding Chinese translation work into ordinary doc sync.
- Updating generated files by hand when a generator or sync script owns them.

## Rules

- User-facing docs match implementation.
- Sync sibling docs repos such as HeavenBase-docs when public behavior changes there.
- Update architecture notes, rule examples, capability matrices, progress trackers, and generated docs when their claims change.
- Regenerate generated docs when the repo provides generators.
- For Mintlify docs, follow the target docs guide: `docs.json`, numbered title-case headings, `<br/>` section separators, language-tagged code fences, root-relative links, and navigation updates.
- For Chinese (`zh/`) Mintlify pages, load [../../tasks/doc-trans.md](../../tasks/doc-trans.md); do not fold translation into ordinary doc sync.

## Related rules

Also apply [test.md](test.md) when examples need verification, [review.md](review.md) for completion reporting, and [../../tasks/doc-sync.md](../../tasks/doc-sync.md) for docs workflow.
