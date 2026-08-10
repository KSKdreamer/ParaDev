---
id: doc-trans
task_kind: doc-trans
status: active
enabled: true
order: 32
keywords: [translate docs, zh docs, chinese translation, batch translate, re-translate, doc translation, line-aligned translation]
triggers: [translate, translation, zh doc, chinese docs, batch translate, re-translate, line-by-line translation, doc-trans]
description: Use when translating or re-translating English MDX docs into line-aligned Chinese pages.
related_rules: [overview, docs, test]
---

# Doc Translation Task

## Goal

Produce faithful Chinese (`zh/`) Mintlify pages from canonical English MDX. Translation is a separate workflow from [doc-sync.md](doc-sync.md): English docs change in doc-sync; zh pages refresh here only when explicitly requested.

## When to use

Load this task when the user asks to:

- translate docs, sync `zh/`, or batch-translate a nav section
- re-translate after English pages changed
- drop legacy Chinese stubs and replace them with line-aligned translations

Do **not** use this task during normal English doc sync. If English changed and `zh/` is stale, report stale paths and recommend a doc-trans pass.

## Sources

1. Load the `mintlify` skill when available for Mintlify components, `docs.json`, and validation commands.
2. Read the target docs repo `AGENTS.md`, `docs.json`, and the English source page(s).
3. Resolve translation terminology from the first available glossary source (see **Translation terminology** below).
4. Read 2-3 nearby English MDX pages and any existing `zh/` pair for voice and navigation context.
5. Verify facts against code/tests when the English page describes behavior. Do not invent shipped features.

## Hard constraints

These are non-negotiable:

1. **Total line parity:** each `zh/` file must have exactly the same number of lines as its English source file.
2. **Section line parity:** line counts must match within every section and subsection bounded by headings (`##`, `###`, …), not only at file level. A section that spans English lines 20–45 must span the same line numbers in zh.
3. **One-to-one line map:** English line *N* maps to zh line *N*, including blank lines, frontmatter delimiters, JSX tags, code fences, table rows, list markers, and `<br/>` separators.
4. **Code parity:** every code fence must keep the same language tag, fence boundaries, and executable content byte-for-byte. Do not translate code, commands, flags, env vars, identifiers, paths, URLs, JSON/YAML keys, or API literals inside fences.
5. **Structure parity:** preserve heading numbers, component names, link targets, anchors, and navigation paths. Translate link text only when the line stays aligned and the target URL/path is unchanged.

## Voice and fidelity

Within the line constraints above:

- Translate **line-by-line**. Work through the English file in order; do not rewrite the page as a free summary.
- Write like a **native Chinese technical writer**: professional, friendly, direct. Prefer natural 中文 over literal calques when the meaning stays the same.
- You may **reorder phrases inside a sentence** or use more local wording when it reads better in Chinese.
- Every translated line must convey the **same information** as the matching English line at sentence level. Do not omit, add, or soften claims to fit line length; adjust wording instead.
- Translate prose, table cell descriptions, callout bodies, and comments (including MDX comments and code comments). Keep comment markers (`#`, `//`, `{/* */}`) unchanged.
- Never translate frontmatter keys, product names listed in the resolved glossary, or proper nouns that readers expect in English (`HeavenBase`, `Mintlify`, `MCP`, …).

## File policy

- **Drop legacy zh first** when the user asks for a batch re-translation. Delete or fully replace stale `zh/` pages in the target scope; do not patch line-by-line over outdated structure.
- Mirror English paths under `zh/` (for example `features/workspace.mdx` → `zh/features/workspace.mdx`).
- Update `docs.json` only when translation scope includes navigation labels or new zh pages. Nav structure should already exist from English/doc-sync work.
- Do not move English files unless the user explicitly requests a restructure.

## Workflow

1. Identify the English page set (nav group, directory, or explicit file list).
2. Read each English source end-to-end. Note sections, code blocks, and line boundaries.
3. Delete or overwrite the matching legacy `zh/` files in scope.
4. Translate line-by-line into `zh/`, preserving structure. Prefer editing in aligned pairs (English left, zh right) or writing zh from a line-numbered English copy.
5. Run verification (below). Fix any line, section, or code-block mismatch before reporting done.
6. Run docs checks when available: `mint validate`, `mint broken-links`, and repo wrappers.
7. Report translated files, dropped legacy files, line-count verification output, and any English pages left untranslated.

## Verification

Before completion, verify every EN/zh pair in scope:

```python
from pathlib import Path
import re

def verify_pair(en_path: str, zh_path: str) -> bool:
    en_lines = Path(en_path).read_text(encoding="utf-8").splitlines()
    zh_lines = Path(zh_path).read_text(encoding="utf-8").splitlines()
    if len(en_lines) != len(zh_lines):
        return False
    en_blocks = re.findall(r"```(\w*)\n(.*?)```", Path(en_path).read_text(encoding="utf-8"), re.S)
    zh_blocks = re.findall(r"```(\w*)\n(.*?)```", Path(zh_path).read_text(encoding="utf-8"), re.S)
    if len(en_blocks) != len(zh_blocks):
        return False
    for (et, eb), (zt, zb) in zip(en_blocks, zh_blocks):
        if et != zt or eb != zb:
            return False
    return True
```

Also spot-check:

- section headings still numbered and aligned
- `<br/>` separators present on the same lines as English
- callout/component tags unchanged
- Further Exploration links still root-relative and target-correct

Report `mint validate` result when the docs repo supports it.

## Chinese formatting

- Use corner brackets 「」 for quoted phrases in Chinese prose.
- On first mention, in headings, emphasis, or when paired with code identifiers, append the English original in parentheses: 入口 (Gateway), 端点 (Endpoint), 预设 (Preset), 工作区 (Workspace).
- **Agent** may appear as 智能体 or as **Agent** when emphasizing the product concept.

## Translation terminology

Read and apply the first available glossary source before translating:

1. `{docs-repo}/_docs-guide/terminology.md`
2. `{docs-repo}/reference/glossary.mdx` (or the repo's published glossary page)
3. Default fallback: [../../assets/default-glossary.md](../../assets/default-glossary.md) in this heaven-style skill

Use those labels consistently unless the English page uses a different deliberate label. Keep English tokens for identifiers readers see in code. Report which glossary source you used.

## Handoff from doc-sync

When English pages change:

- doc-sync updates English and `docs.json`; it reports stale `zh/` paths.
- doc-trans re-translates affected pairs using the latest English file as the single source of truth.
- If English line count changes, zh must be re-translated to match; partial zh edits that break line parity are not acceptable.
