---
id: doc-sync
task_kind: doc-sync
status: active
enabled: true
order: 30
keywords: [sync docs, update docs, heavenbase docs, mintlify docs, docs json, documentation task]
triggers: [doc sync, update documentation, sync HeavenBase-docs, update Mintlify, docs out of date]
description: Use when syncing English code-facing docs, Mintlify MDX pages, navigation, or sibling docs repos with current implementation.
related_rules: [overview, docs, test, config, util, model, extension]
---

# Doc Sync Task

## Goal

Keep HeavenBase English documentation accurate, readable, and navigable after code or architecture changes.

## Sources

1. If the `mintlify` skill is installed or listed as available, load it before editing Mintlify docs. Treat it as the live source for `docs.json`, components, links, CLI validation, and current Mintlify conventions.
2. Read the target docs repo `AGENTS.md`, `_docs-guide/AGENTS.md`, and `docs.json`.
3. Resolve terminology from the first available glossary source when naming public concepts or flagging translation staleness:
   - `{docs-repo}/_docs-guide/terminology.md`
   - `{docs-repo}/reference/glossary.mdx` (or the repo's published glossary page)
   - Default fallback: [../../assets/default-glossary.md](../../assets/default-glossary.md) in this heaven-style skill
4. Read 2-3 nearby MDX pages to match voice, headings, examples, and navigation.
5. Verify behavior against the current codebase, tests, generated docs, and examples in the relevant rules. Do not claim planned behavior as shipped.

## Language Scope

- Default to English docs only: update canonical English MDX pages and `docs.json` navigation.
- Do not update `zh/` during doc sync. If English changes make `zh/` stale, report the stale paths and hand off to [doc-trans.md](doc-trans.md).
- Chinese translation uses a separate task with strict line alignment and different acceptance criteria.

## Page Format

Use the target repo guide when it differs, otherwise default to this structure:

````mdx
---
title: "Clear page title"
description: "One-line SEO and navigation description."
---

<Note>
    A short one-liner that captures the page's core idea.
</Note>

## 1. First Section

Friendly, professional, intuitive explanation before commands or code.

```python
import heavenbase as hb
```

<br/>

## 2. Second Section

Practical content with realistic values and working code demos.

<br/>

## Summary

- What the reader should remember.
- What they can do next.

<br/>

## Further Exploration

<Tip>
    **Related resources:**
    - [Related page](/features/configuration) - Why it matters here.
</Tip>

<br/>
````

## Formatting Criteria

- Frontmatter must include `title` and `description`.
- Start with a short note/callout when the page has a clear design idea.
- Use numbered subtitles: `## 1. Section`, `### 1.1. Subsection`.
- Use title case for section and subsection headings (capitalize major words; keep articles, conjunctions, and short prepositions lowercase unless first in the heading), for example `Further Exploration` and `Try It Out`, not sentence case.
- Do not number `Summary` or `Further Exploration`.
- End every section and subsection with `<br/>`.
- Use second person, active voice, and concise explanations. Avoid marketing language and filler.
- Explain what something is before how to use it.
- Include realistic code demos with language-tagged fences; test examples when practical.
- Use root-relative internal links without file extensions.
- Add new pages to `docs.json` navigation.

## Workflow

1. Identify which code/API/config/docs claims changed.
2. Decide whether to update an existing English page or add a new English page.
3. Update MDX content, examples, callouts, links, and `docs.json` navigation.
4. Sync sibling docs repos such as `HeavenBase-docs` when public behavior changed there.
5. Run docs checks when available: `mint validate`, `mint broken-links`, and any repo wrappers.
6. Report updated pages, navigation changes, stale translation pages, verification commands, and any unverified TODOs.
