# Autocomplete Latency Benchmark Progress

Date: 2026-06-13 16:59

Linear: none

## Done

- Benchmarked CodeMirror completion request construction, JSON body creation, backend completion context scanning, and catalog-backed completion.
- Root cause: frontend text serialization was small, but backend completion without cursor `offset` walked from the start of the document to infer context. Synthetic documents measured about 16 ms at 132 KB, 83 ms at 672 KB, 166 ms at 1.35 MB, and 334 ms at 2.7 MB.
- Added `implicitCompletionMaxLength` with a 50 KB default so CodeMirror skips implicit backend completion for large buffers; explicit completion still works.
- Added optional completion `offset` through TypeScript, REST, Tauri, stdio payloads, CLI, and the SDK helper. With `offset`, the backend uses a bounded near-cursor context scan.
- Cached catalog completion rows by SQLite path, mtime, and size so repeated suggestions do not reread the catalog database.

## Verification

- Targeted frontend helper test passed: `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/pdxLsp.test.ts`.
- Targeted LSP tests passed for catalog cache, completion contexts, REST route, stdio payload, and offset performance.
- Post-change benchmark with `offset`: about 3.1-3.5 ms for the same 132 KB, 672 KB, 1.35 MB, and 2.7 MB synthetic documents, including cached catalog-backed completion.

## Risks Or Blockers

- Standard LSP `textDocument/completion` clients only provide line/character, so they keep the slower fallback unless they use ParaDev's payload side channel or a future document-state index.
- The bounded near-cursor scan intentionally favors responsiveness. Very large blocks with context keys more than 50 KB before the cursor may need explicit syntax-aware indexing later.

## Next

- Add per-open-document context indexes in the stdio LSP server so standard LSP clients also get fast completion without non-standard `offset`.
- Consider local static keyword completions in the editor for large implicit buffers, with backend completion reserved for explicit requests.
