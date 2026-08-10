# Assets

Static bundles and **read-only reference trees** for agents (not loaded unless needed).

## default-glossary.md

Bundled en–zh terminology table for doc-sync and doc-trans.
Project glossary files take precedence (`_docs-guide/terminology.md`, `reference/glossary.mdx`); when those are absent, use this fallback.

## heavenbase-reference/

Shallow git clone of the HeavenBase repository for ground-truth patterns (`AGENTS.md`, `src/`, `demos/`, `scripts/`).

Refresh:

```bash
python scripts/sync.py
python scripts/index.py
```

The clone is gitignored. `python scripts/install.py` refreshes an existing clone or creates it when absent, then regenerates the index.

When `heaven-style` is embedded in the HeavenBase repository itself, do **not** host this clone in-repo (it loops with skill maintenance). Use the standard global install at `~/.agents/skills/heaven-style` instead; install it from Blueprint with `rtk uv run python .agents/skills/heaven-style/scripts/install.py`. `install.py` skips reference sync automatically in the embedded layout.
